import paramiko
import os
import sys

HOSTNAME = "8.215.23.17"
USERNAME = "root"
PASSWORD = "N!colay_No1r.Ai@Agent#Secure"

def execute_remote(cmd, hide_output=False):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)
        
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if not hide_output:
            if out: print(f"STDOUT:\n{out}")
            if err: print(f"STDERR:\n{err}")
            
        ssh.close()
        return out, err
    except Exception as e:
        print(f"[!] Gagal eksekusi remote: {e}")
        return None, str(e)

def upload_file(local_path, remote_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, timeout=10)
        
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()
        print(f"[+] Berhasil mengupload {local_path} ke {remote_path}")
        return True
    except Exception as e:
        print(f"[!] Gagal upload: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        print(f"[*] Menjalankan: {command}")
        execute_remote(command)
    else:
        print("Gunakan: python vps_htb_bridge.py '<command>'")
