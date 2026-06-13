import sys
sys.path.append('c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-vps')
import vps_htb_bridge

# Step 1: Hapus log lama
vps_htb_bridge.execute_remote("rm -f /root/htb_sandbox/dvwa_attack_live.log /root/htb_sandbox/dvwa_attack.log")

# Step 2: Jalankan secara sinkron langsung via paramiko (bukan nohup)
# Ini akan streaming langsung ke stdout kita
print("[*] Menjalankan dvwa_attacker v3 secara sinkron di VPS...")
print("[*] Output akan muncul setelah selesai...")
out, err = vps_htb_bridge.execute_remote("cd /root/htb_sandbox && python3 dvwa_attacker.py")
print(out)
if err:
    print("STDERR:", err[:1000])
