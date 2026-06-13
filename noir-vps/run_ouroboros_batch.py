import sys
sys.path.append('c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-vps')
import vps_htb_bridge

print('[*] Mengeksekusi semua payload dalam queue...')
cmd = """
for p in /root/htb_sandbox/payloads_queue/*.py; do
    echo "----------------------------------------"
    echo "Mengeksekusi $p"
    python3 /root/htb_sandbox/ouroboros_core.py "$p"
    rm -f "$p"
done
echo "=== HASIL MEMORI ==="
ls -la /root/htb_sandbox/memories/
"""
out, err = vps_htb_bridge.execute_remote(cmd)
print(out)
if err: print('STDERR:', err[:500])
