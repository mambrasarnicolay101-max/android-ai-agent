import sys
sys.path.append('c:/Users/ASUS/.gemini/antigravity/scratch/android-ai-agent/noir-vps')
import vps_htb_bridge

# Setup DVWA database langsung via MySQL di dalam container
script = """
echo "=== Step 1: Inisialisasi MySQL di container DVWA ==="
docker exec dvwa_target mysql -u root --password=p@ssw0rd dvwa -e "SELECT 1;" 2>/dev/null && echo "MySQL OK" || echo "MySQL perlu init"

echo "=== Step 2: Coba create DB via setup.php dengan cookie ==="
curl -s -c /tmp/c.txt http://localhost:9090/setup.php > /dev/null
TOKEN=$(curl -s -b /tmp/c.txt -c /tmp/c.txt http://localhost:9090/setup.php | grep -oP "user_token.*?value='\\K[^']+")
echo "Setup token: $TOKEN"
curl -s -b /tmp/c.txt -c /tmp/c.txt http://localhost:9090/setup.php \
  -X POST -d "create_db=Create+%2F+Reset+Database&user_token=$TOKEN" | grep -iE 'success|created|error' | head -5

echo "=== Step 3: Test login setelah setup ==="
sleep 2
TOKEN2=$(curl -s -c /tmp/c2.txt http://localhost:9090/login.php | grep -oP "name='user_token' value='\\K[^']+")
echo "Login token: $TOKEN2"
RESP=$(curl -s -c /tmp/c2.txt -b /tmp/c2.txt -X POST http://localhost:9090/login.php \
  -d "username=admin&password=password&Login=Login&user_token=$TOKEN2" -D -)
echo "$RESP" | grep -E "Location:|HTTP/"
curl -s -b /tmp/c2.txt http://localhost:9090/index.php | grep -iE "welcome|logout|DVWA Security" | head -3
"""
out, err = vps_htb_bridge.execute_remote(script)
print(out)
if err:
    print("ERR:", err[:500])
