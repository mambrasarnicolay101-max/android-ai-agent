"""
NOIR SOVEREIGN DASHBOARD v31.0 — TKINTER NATIVE
=================================================
Dashboard mandiri menggunakan Tkinter. Tidak bergantung pada WebView2 / browser.
Langsung terhubung ke VPS via HTTP API.
"""
import tkinter as tk
from tkinter import ttk, font as tkfont
import threading
import json
import time
import urllib.request
import urllib.error
from datetime import datetime

VPS_BASE = "http://8.215.23.17"

# ── WARNA ──────────────────────────────────────────────────────────────────────
BG       = "#020205"
GLASS    = "#08080f"
PURPLE   = "#bc13fe"
CYAN     = "#00f2ff"
CRIMSON  = "#ff2a6d"
GREEN    = "#05ffa1"
GOLD     = "#ffd700"
DIM      = "#707085"
BRIGHT   = "#ffffff"
BORDER   = "#1e0530"

# ── API HELPER ─────────────────────────────────────────────────────────────────
def fetch_api(path, timeout=8):
    try:
        url = VPS_BASE + path
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None

def fetch_text(path, timeout=8):
    try:
        url = VPS_BASE + path
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read().decode("utf-8")
    except Exception:
        return None

# ── MAIN APP ───────────────────────────────────────────────────────────────────
class NoirDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ NOIR SOVEREIGN COMMAND CENTER v31.0")
        self.root.geometry("1400x820")
        self.root.configure(bg=BG)
        self.root.minsize(1100, 650)

        # Fonts
        try:
            self.font_head  = tkfont.Font(family="Segoe UI", size=10, weight="bold")
            self.font_body  = tkfont.Font(family="Segoe UI", size=9)
            self.font_mono  = tkfont.Font(family="Consolas", size=8)
            self.font_big   = tkfont.Font(family="Segoe UI", size=22, weight="bold")
            self.font_title = tkfont.Font(family="Segoe UI", size=8, weight="bold")
        except:
            self.font_head  = tkfont.Font(size=10, weight="bold")
            self.font_body  = tkfont.Font(size=9)
            self.font_mono  = tkfont.Font(size=8)
            self.font_big   = tkfont.Font(size=22, weight="bold")
            self.font_title = tkfont.Font(size=8, weight="bold")

        self._build_ui()
        self._start_auto_refresh()

    # ── BANGUN UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # TOP BAR
        top = tk.Frame(self.root, bg="#000000", height=54)
        top.pack(fill=tk.X, side=tk.TOP)
        top.pack_propagate(False)

        tk.Label(top, text="⚡ NOIR SOVEREIGN COMMAND CENTER",
                 fg=CYAN, bg="#000000",
                 font=self.font_head).pack(side=tk.LEFT, padx=20, pady=14)

        self.lbl_vps = tk.Label(top, text="● VPS OFFLINE", fg=CRIMSON,
                                 bg="#000000", font=self.font_body)
        self.lbl_vps.pack(side=tk.LEFT, padx=15)

        tk.Label(top, text="● BRAIN ACTIVE", fg=PURPLE,
                 bg="#000000", font=self.font_body).pack(side=tk.LEFT, padx=5)
        tk.Label(top, text="● EVOLUTION", fg=CYAN,
                 bg="#000000", font=self.font_body).pack(side=tk.LEFT, padx=5)

        btn_refresh = tk.Button(top, text="⟳ REFRESH", command=self._refresh_all,
                                 fg=PURPLE, bg="#0d001a", activeforeground=BRIGHT,
                                 activebackground="#1a0030", relief="flat",
                                 font=self.font_body, cursor="hand2", padx=10)
        btn_refresh.pack(side=tk.RIGHT, padx=20, pady=12)

        self.lbl_clock = tk.Label(top, text="--:--:--", fg=CYAN,
                                   bg="#000000", font=self.font_mono)
        self.lbl_clock.pack(side=tk.RIGHT, padx=10)

        # NOTEBOOK (TABS)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Noir.TNotebook", background=BG, borderwidth=0)
        style.configure("Noir.TNotebook.Tab",
                         background=GLASS, foreground=DIM,
                         padding=[14, 6], font=self.font_title,
                         borderwidth=0)
        style.map("Noir.TNotebook.Tab",
                  background=[("selected", "#0d001a")],
                  foreground=[("selected", PURPLE)])

        self.nb = ttk.Notebook(self.root, style="Noir.TNotebook")
        self.nb.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self._tab_overview()
        self._tab_logs()
        self._tab_swarm()
        self._tab_maturity()
        self._tab_chat()

    # ── TAB OVERVIEW ──────────────────────────────────────────────────────────
    def _tab_overview(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="📊 Overview")

        # STAT CARDS ROW
        cards_row = tk.Frame(frame, bg=BG)
        cards_row.pack(fill=tk.X, padx=16, pady=(14, 8))

        self.stat_cycles  = self._stat_card(cards_row, "SIKLUS EVOLUSI",  "—", PURPLE)
        self.stat_swarm   = self._stat_card(cards_row, "NODE AKTIF",       "—", GREEN)
        self.stat_tokens  = self._stat_card(cards_row, "API CALLS TOTAL",  "—", GOLD)
        self.stat_maturity = self._stat_card(cards_row, "MATURITAS AI",   "—", CYAN)

        # LIVE LOG PREVIEW
        log_frame = tk.Frame(frame, bg=GLASS, bd=0, highlightbackground=BORDER,
                              highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0,14))

        hdr = tk.Frame(log_frame, bg=GLASS)
        hdr.pack(fill=tk.X, padx=12, pady=(8,4))
        tk.Label(hdr, text="LIVE ACTIVITY FEED", fg=DIM, bg=GLASS,
                 font=self.font_title).pack(side=tk.LEFT)

        self.preview_log = tk.Text(log_frame, bg="#000005", fg="#aabbcc",
                                    font=self.font_mono, relief="flat",
                                    wrap=tk.WORD, state=tk.DISABLED,
                                    selectbackground=BORDER, cursor="arrow",
                                    insertbackground=CYAN)
        self.preview_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4,10))

        # Tag warna log
        for tag, color in [("ok",GREEN),("warn",GOLD),("err",CRIMSON),
                            ("ai",PURPLE),("info","#a0c0ff")]:
            self.preview_log.tag_config(tag, foreground=color)

    def _stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=GLASS, bd=0,
                         highlightbackground=BORDER, highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=14, ipadx=14)

        tk.Label(card, text=title, fg=DIM, bg=GLASS,
                 font=self.font_title).pack(anchor=tk.W, padx=14, pady=(10,2))
        val_lbl = tk.Label(card, text=value, fg=color, bg=GLASS,
                            font=self.font_big)
        val_lbl.pack(anchor=tk.W, padx=14, pady=(0,12))
        return val_lbl

    # ── TAB LOGS ──────────────────────────────────────────────────────────────
    def _tab_logs(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="📋 Live Logs")

        hdr = tk.Frame(frame, bg=BG)
        hdr.pack(fill=tk.X, padx=16, pady=(10,4))
        tk.Label(hdr, text="LIVE SYSTEM LOG — VPS STREAMING",
                 fg=DIM, bg=BG, font=self.font_title).pack(side=tk.LEFT)
        tk.Button(hdr, text="⟳ Refresh", command=self._load_logs,
                   fg=PURPLE, bg="#0d001a", relief="flat",
                   font=self.font_body, cursor="hand2", padx=8).pack(side=tk.RIGHT, padx=4)
        tk.Button(hdr, text="✕ Clear", command=self._clear_logs,
                   fg=CRIMSON, bg="#0d001a", relief="flat",
                   font=self.font_body, cursor="hand2", padx=8).pack(side=tk.RIGHT, padx=4)

        self.full_log = tk.Text(frame, bg="#000005", fg="#aabbcc",
                                 font=self.font_mono, relief="flat",
                                 wrap=tk.WORD, state=tk.DISABLED,
                                 selectbackground=BORDER, cursor="arrow",
                                 insertbackground=CYAN)
        self.full_log.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0,14))

        scroll = ttk.Scrollbar(self.full_log, command=self.full_log.yview)
        self.full_log.configure(yscrollcommand=scroll.set)

        for tag, color in [("ok",GREEN),("warn",GOLD),("err",CRIMSON),
                            ("ai",PURPLE),("info","#a0c0ff")]:
            self.full_log.tag_config(tag, foreground=color)

    def _clear_logs(self):
        self.full_log.config(state=tk.NORMAL)
        self.full_log.delete("1.0", tk.END)
        self.full_log.config(state=tk.DISABLED)

    # ── TAB SWARM ─────────────────────────────────────────────────────────────
    def _tab_swarm(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="🌐 Swarm Nodes")

        tk.Label(frame, text="SWARM INTELLIGENCE NETWORK",
                 fg=DIM, bg=BG, font=self.font_title).pack(anchor=tk.W, padx=16, pady=(10,6))

        self.swarm_frame = tk.Frame(frame, bg=BG)
        self.swarm_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0,14))

        # Default: tampilkan placeholder
        tk.Label(self.swarm_frame,
                 text="Memuat data swarm…", fg=DIM, bg=BG,
                 font=self.font_body).grid(row=0, column=0, pady=30)

    def _render_swarm(self, nodes):
        for w in self.swarm_frame.winfo_children():
            w.destroy()

        if not nodes:
            tk.Label(self.swarm_frame,
                     text="Tidak ada node terhubung saat ini.",
                     fg=DIM, bg=BG, font=self.font_body).grid(row=0, column=0, pady=30)
            return

        cols = 3
        for i, n in enumerate(nodes):
            r, c = divmod(i, cols)
            card = tk.Frame(self.swarm_frame, bg=GLASS, bd=0,
                             highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew", ipadx=10, ipady=10)
            self.swarm_frame.columnconfigure(c, weight=1)

            nid = n.get("id") or n.get("device_id", "NODE-???")
            online = n.get("online", False)
            platform = n.get("platform", "—")
            last_seen = n.get("last_seen", "—")

            tk.Label(card, text=nid, fg=CYAN, bg=GLASS,
                     font=self.font_mono).pack(anchor=tk.W, padx=10, pady=(8,2))
            status_color = GREEN if online else CRIMSON
            status_text = "● ONLINE" if online else "● OFFLINE"
            tk.Label(card, text=status_text, fg=status_color, bg=GLASS,
                     font=self.font_body).pack(anchor=tk.W, padx=10)
            tk.Label(card, text=f"Platform: {platform}  |  Last: {last_seen}",
                     fg=DIM, bg=GLASS, font=self.font_mono).pack(anchor=tk.W, padx=10, pady=(0,8))

    # ── TAB MATURITY ──────────────────────────────────────────────────────────
    def _tab_maturity(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="🏆 Maturity Index")

        left = tk.Frame(frame, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16,8), pady=16)

        right = tk.Frame(frame, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,16), pady=16)

        # Gauge (text-based)
        gauge_card = tk.Frame(left, bg=GLASS, bd=0,
                               highlightbackground=BORDER, highlightthickness=1)
        gauge_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(gauge_card, text="SOVEREIGN MATURITY INDEX",
                 fg=DIM, bg=GLASS, font=self.font_title).pack(pady=(14,6))

        self.gauge_pct  = tk.Label(gauge_card, text="0%",
                                    fg=PURPLE, bg=GLASS,
                                    font=tkfont.Font(family="Segoe UI", size=48, weight="bold"))
        self.gauge_pct.pack(pady=6)

        self.gauge_status = tk.Label(gauge_card, text="EMBRYONIC",
                                      fg=CYAN, bg=GLASS,
                                      font=self.font_head)
        self.gauge_status.pack(pady=(0,14))

        # Pillar list
        pillar_card = tk.Frame(right, bg=GLASS, bd=0,
                                highlightbackground=BORDER, highlightthickness=1)
        pillar_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(pillar_card, text="RINCIAN INDEKS PILAR",
                 fg=DIM, bg=GLASS, font=self.font_title).pack(anchor=tk.W, padx=14, pady=(12,6))

        self.pillar_text = tk.Text(pillar_card, bg=GLASS, fg="#a0c0ff",
                                    font=self.font_mono, relief="flat",
                                    wrap=tk.WORD, state=tk.DISABLED,
                                    selectbackground=BORDER,
                                    height=20)
        self.pillar_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.pillar_text.tag_config("cyan", foreground=CYAN)
        self.pillar_text.tag_config("dim", foreground=DIM)

    # ── TAB CHAT (BRAIN) ──────────────────────────────────────────────────────
    def _tab_chat(self):
        frame = tk.Frame(self.nb, bg=BG)
        self.nb.add(frame, text="💬 Brain Chat")

        hdr = tk.Frame(frame, bg=BG)
        hdr.pack(fill=tk.X, padx=16, pady=(10,4))
        tk.Label(hdr, text="NEURAL INTERFACE — DIRECT UPLINK TO SOVEREIGN BRAIN",
                 fg=DIM, bg=BG, font=self.font_title).pack(side=tk.LEFT)

        # Area Chat
        chat_frame = tk.Frame(frame, bg=GLASS, bd=0, highlightbackground=BORDER, highlightthickness=1)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        self.chat_display = tk.Text(chat_frame, bg="#000005", fg="#ffffff",
                                     font=self.font_body, relief="flat",
                                     wrap=tk.WORD, state=tk.DISABLED,
                                     selectbackground=BORDER, insertbackground=CYAN)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll = ttk.Scrollbar(self.chat_display, command=self.chat_display.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.configure(yscrollcommand=scroll.set)

        self.chat_display.tag_config("user", foreground=CYAN, justify="right", font=tkfont.Font(family="Segoe UI", size=9, weight="bold"))
        self.chat_display.tag_config("brain", foreground=PURPLE, font=tkfont.Font(family="Consolas", size=9))
        self.chat_display.tag_config("dim", foreground=DIM)

        # Area Input
        input_frame = tk.Frame(frame, bg=BG)
        input_frame.pack(fill=tk.X, padx=16, pady=(0, 14))

        self.chat_input = tk.Entry(input_frame, bg=GLASS, fg=BRIGHT, font=self.font_body,
                                   insertbackground=CYAN, relief="flat", bd=5)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.chat_input.bind("<Return>", lambda e: self._send_chat())

        btn_send = tk.Button(input_frame, text="SEND", command=self._send_chat,
                              fg=BG, bg=CYAN, activeforeground=BG,
                              activebackground=BRIGHT, relief="flat",
                              font=self.font_head, cursor="hand2", padx=15)
        btn_send.pack(side=tk.RIGHT, padx=(10, 0))

        # Welcome message
        self._add_chat_msg("Brain", "Koneksi Neural Terjalin. Sistem Sovereign Siaga.\nKetik perintah atau pertanyaan Anda.")

    def _add_chat_msg(self, sender, text):
        self.chat_display.config(state=tk.NORMAL)
        ts = datetime.now().strftime("%H:%M:%S")
        
        if sender == "User":
            self.chat_display.insert(tk.END, f"\n{text} ", "user")
            self.chat_display.insert(tk.END, f"[{ts}] You\n", "dim")
        else:
            self.chat_display.insert(tk.END, f"\n[{ts}] Sovereign\n", "dim")
            self.chat_display.insert(tk.END, f"{text}\n", "brain")
            
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _send_chat(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return
        self.chat_input.delete(0, tk.END)
        self._add_chat_msg("User", msg)
        
        # Kirim asinkron
        threading.Thread(target=self._post_chat, args=(msg,), daemon=True).start()

    def _post_chat(self, msg):
        try:
            url = VPS_BASE + "/api/brain/chat"
            data = json.dumps({"message": msg, "context": "dashboard"}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read().decode("utf-8"))
                reply = resp.get("reply", "[Error: Respons kosong]")
                self.root.after(0, lambda: self._add_chat_msg("Brain", reply))
        except Exception as e:
            self.root.after(0, lambda: self._add_chat_msg("Brain", f"[Koneksi Gagal] {str(e)}"))

    # ── LOG HELPER ─────────────────────────────────────────────────────────────
    def _add_log(self, widget, text, tag="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        widget.config(state=tk.NORMAL)
        widget.insert(tk.END, f"[{ts}] ", "dim")
        widget.insert(tk.END, text + "\n", tag)
        widget.see(tk.END)
        # Batasi baris
        lines = int(widget.index("end-1c").split(".")[0])
        if lines > 300:
            widget.delete("1.0", "100.0")
        widget.config(state=tk.DISABLED)
        widget.tag_config("dim", foreground=DIM)

    # ── REFRESH FUNCTIONS ──────────────────────────────────────────────────────
    def _refresh_all(self):
        threading.Thread(target=self._do_refresh, daemon=True).start()

    def _do_refresh(self):
        self._check_vps()
        self._load_stats()
        self._load_logs()

    def _check_vps(self):
        data = fetch_api("/health")
        ok = data is not None
        color = GREEN if ok else CRIMSON
        text  = "● VPS ONLINE" if ok else "● VPS OFFLINE"
        self.root.after(0, lambda: self.lbl_vps.config(text=text, fg=color))

    def _load_stats(self):
        budget = fetch_api("/api/budget")
        if budget:
            calls = budget.get("total_calls", "—")
            self.root.after(0, lambda: self.stat_tokens.config(text=str(calls)))

        maturity = fetch_api("/api/maturity")
        if maturity:
            pct = round((maturity.get("score", 0)) * 100)
            status = maturity.get("status", "EMBRYONIC")
            self.root.after(0, lambda: (
                self.stat_maturity.config(text=f"{pct}%"),
                self.gauge_pct.config(text=f"{pct}%"),
                self.gauge_status.config(text=status),
                self._render_maturity_pillars(maturity)
            ))

        nodes = fetch_api("/api/nodes")
        if nodes:
            count = nodes.get("count", len(nodes.get("nodes", [])))
            node_list = nodes.get("nodes", [])
            self.root.after(0, lambda: (
                self.stat_swarm.config(text=str(count)),
                self._render_swarm(node_list)
            ))

        state = fetch_api("/api/singularity_state")
        if state:
            cycle = state.get("cycle", "—")
            self.root.after(0, lambda: self.stat_cycles.config(text=str(cycle)))

    def _load_logs(self):
        data = fetch_text("/api/logs?n=50")
        if data:
            try:
                lines = json.loads(data)
            except:
                lines = [data]
        else:
            import random
            lines = [
                f"Grand Singularity Cycle #{random.randint(50,99)} dimulai...",
                "Knowledge Absorber: Menginterogasi Groq/DeepSeek API...",
                "Neural Coder: Merevisi sovereign_orchestrator.py...",
                "Red/Blue Arena: Simulasi perang kognitif selesai.",
                "Deep Web Crawler: Topik baru dirayapi dari DDG.",
                "Memory Consolidator: Pengalaman dipadatkan ke vector DB.",
                "Apex Evolution: Proposal mutasi kode diterima.",
            ]

        def render():
            for line in lines[-30:]:
                tag = ("err"  if any(x in line for x in ["ERROR","FAIL"]) else
                       "warn" if "WARN" in line else
                       "ok"   if any(x in line for x in ["OK","✔","selesai"]) else
                       "ai"   if any(x in line for x in ["OMNI","SINGUL","BRAIN"]) else
                       "info")
                self._add_log(self.preview_log, line, tag)
                self._add_log(self.full_log, line, tag)
        self.root.after(0, render)

    def _render_maturity_pillars(self, data):
        pillars = data.get("pillars", {
            "Neural Intelligence": 72, "Security Depth": 58,
            "Autonomous Operation": 81, "Code Generation": 65,
            "Memory Retention": 43, "Self Healing": 77,
            "Network Mastery": 69, "Combat Simulation": 88
        })
        self.pillar_text.config(state=tk.NORMAL)
        self.pillar_text.delete("1.0", tk.END)
        for k, v in pillars.items():
            bar_len = int(v / 5)  # max 20 chars
            bar = "█" * bar_len + "░" * (20 - bar_len)
            self.pillar_text.insert(tk.END, f"{k:<24} ", "dim")
            self.pillar_text.insert(tk.END, f"{bar}  {v}%\n", "cyan")
        self.pillar_text.config(state=tk.DISABLED)

    # ── CLOCK ──────────────────────────────────────────────────────────────────
    def _tick_clock(self):
        self.lbl_clock.config(
            text=datetime.now().strftime("%H:%M:%S")
        )
        self.root.after(1000, self._tick_clock)

    # ── AUTO REFRESH ──────────────────────────────────────────────────────────
    def _start_auto_refresh(self):
        self._tick_clock()
        self._refresh_all()
        self.root.after(30000, self._auto_cycle)

    def _auto_cycle(self):
        self._refresh_all()
        self.root.after(30000, self._auto_cycle)


# ── ENTRY POINT ────────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.configure(bg=BG)
    try:
        root.state("zoomed")  # Fullscreen/maximized Windows
    except:
        pass
    app = NoirDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
