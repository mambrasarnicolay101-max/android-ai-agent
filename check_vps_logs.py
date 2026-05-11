import paramiko

VPS_IP = '8.215.23.17'
VPS_USER = 'root'
VPS_PASS = 'N!colay_No1r.Ai@Agent#Secure'

def check_logs():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_IP, username=VPS_USER, password=VPS_PASS)
        
        print("--- NOIR-DASHBOARD LOGS ---")
        stdin, stdout, stderr = ssh.exec_command('docker logs --tail 50 noir-dashboard')
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
        print("\n--- NOIR-BRAIN LOGS ---")
        stdin, stdout, stderr = ssh.exec_command('docker logs --tail 50 noir-brain')
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_logs()
