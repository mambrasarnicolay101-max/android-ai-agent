import os
import paramiko

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('"+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+"', username='root', password='N!colay_No1r.Ai@Agent#Secure')

print("[*] Restarting noir-dashboard...")
i, o, e = s.exec_command('docker restart noir-dashboard')
print(o.read().decode())

print("[*] Container status:")
i2, o2, e2 = s.exec_command('docker ps --format "table {{.Names}}\t{{.Status}}"')
print(o2.read().decode())

s.close()
print("[DONE] Deployment complete — v21.0.3 LIVE")

