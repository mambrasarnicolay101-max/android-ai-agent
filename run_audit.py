"""
NOIR SOVEREIGN SYSTEM AUDIT SCRIPT
Scans all Python modules for bugs, missing imports, conflicts, and issues.
"""
import os, re, ast, json

ROOT = "."
VPS_DIR = "noir-vps"
UI_DIR = "noir-ui"

STDLIB = {
    'os','sys','json','time','random','logging','threading','re','base64',
    'subprocess','pathlib','datetime','typing','abc','hashlib','uuid','shutil',
    'functools','collections','io','traceback','ast','copy','math','enum',
    'http','urllib','socket','struct','hmac','inspect','signal','queue',
    'multiprocessing','concurrent','contextlib','warnings','weakref','gc',
    'platform','tempfile','glob','fnmatch','stat','pwd','grp','resource',
    'string','textwrap','itertools','operator','heapq','bisect','array',
    'dataclasses','attrs','pprint','reprlib','numbers','decimal','fractions',
    'cmath','statistics','random','secrets','ssl','select','selectors',
    'asyncio','http','email','html','xml','csv','configparser','argparse',
    'getopt','atexit','sched','calendar','locale','gettext','codecs'
}

KNOWN_THIRD_PARTY = {
    'requests','fastapi','uvicorn','pydantic','httpx','paramiko','scp',
    'dotenv','chromadb','playwright','tensorflow','numpy','pandas','PIL',
    'Crypto','flask','aiofiles','starlette','websockets','youtube_transcript_api',
    'sklearn','scipy','matplotlib','cv2','torch','transformers','openai',
    'anthropic','groq','langchain','sentence_transformers','faiss','hnswlib'
}

issues = {
    "CRITICAL": [],
    "WARNING": [],
    "INFO": []
}

vps_modules = set()
for f in os.listdir(VPS_DIR):
    if f.endswith('.py'):
        vps_modules.add(f.replace('.py',''))

def audit_file(fpath, fname):
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    lines = content.splitlines()

    # 1. SYNTAX CHECK
    try:
        ast.parse(content)
    except SyntaxError as e:
        issues["CRITICAL"].append(f"[SYNTAX_ERROR] {fname}:L{e.lineno} — {e.msg}")
        return  # Can't proceed with more analysis if syntax is broken

    # 2. MISSING IMPORTS
    imports = re.findall(r'^(?:from (\w+)|import (\w+))', content, re.MULTILINE)
    for imp in imports:
        mod = imp[0] or imp[1]
        if not mod: continue
        if mod in STDLIB or mod in KNOWN_THIRD_PARTY: continue
        if mod in vps_modules: continue
        if mod.startswith('_'): continue
        issues["WARNING"].append(f"[MISSING_MODULE] {fname}: imports '{mod}' — not found in noir-vps/")

    # 3. UNDEFINED VARIABLE: logic_steps
    if 'logic_steps' in content:
        defined = bool(re.search(r'logic_steps\s*=', content))
        if not defined:
            issues["CRITICAL"].append(f"[UNDEF_VAR] {fname}: 'logic_steps' is used but never defined — NameError at runtime")

    # 4. DUPLICATE SANDBOX IMPORTS
    if content.count('from sandbox_engine import SandboxEngine') > 1:
        cnt = content.count('from sandbox_engine import SandboxEngine')
        issues["WARNING"].append(f"[DUPLICATE_IMPORT] {fname}: 'SandboxEngine' imported {cnt}x — dead code/confusion")

    # 5. BARE EXCEPT (masks all exceptions)
    for i, line in enumerate(lines, 1):
        if re.match(r'\s*except\s*:\s*$', line) or re.match(r'\s*except\s*:\s*pass\s*$', line):
            issues["WARNING"].append(f"[BARE_EXCEPT] {fname}:L{i} — catches ALL exceptions, hides real errors")

    # 6. INCOMPLETE DICT (missing closing brace before except)
    if re.search(r'"description":\s*"[^"]+",?\s*\n\s*except ', content):
        issues["CRITICAL"].append(f"[SYNTAX_PATTERN] {fname}: JSON dict appears unclosed before 'except' — likely SyntaxError")

    # 7. HARDCODED CREDENTIALS (not from env)
    for i, line in enumerate(lines, 1):
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
            if 'environ' not in line and 'getenv' not in line and 'example' not in line.lower():
                issues["WARNING"].append(f"[HARDCODED_CRED] {fname}:L{i}: {line.strip()[:90]}")

    # 8. STALE PILLAR COUNTS in log messages
    for i, line in enumerate(lines, 1):
        if re.search(r'[89]\s*[Pp]ilar', line) or '8 Pillar' in line:
            issues["INFO"].append(f"[STALE_COUNT] {fname}:L{i}: References old 8/9-pillar count: {line.strip()[:80]}")

    # 9. BLOCKING sleep() on main thread in async context
    if 'uvicorn' in content or 'fastapi' in content:
        for i, line in enumerate(lines, 1):
            if 'time.sleep(' in line and 'async' not in lines[max(0,i-3):i]:
                issues["INFO"].append(f"[ASYNC_BLOCK] {fname}:L{i}: time.sleep() in async context — use asyncio.sleep()")

# --- Run audit ---
print("="*60)
print(" NOIR SOVEREIGN SYSTEM AUDIT")
print("="*60)

for fname in sorted(os.listdir(VPS_DIR)):
    if fname.endswith('.py'):
        audit_file(os.path.join(VPS_DIR, fname), fname)

for fname in sorted(os.listdir(UI_DIR)):
    if fname.endswith('.py'):
        audit_file(os.path.join(UI_DIR, fname), fname)

for fname in ['sovereign_unified_boot.py', 'deploy_to_vps.py', 'purge_system.py']:
    if os.path.exists(fname):
        audit_file(fname, fname)

# --- Report ---
print(f"\n{'='*60}")
print(f" CRITICAL ({len(issues['CRITICAL'])} issues)")
print(f"{'='*60}")
for i in issues["CRITICAL"]:
    print(f"  ✗ {i}")

print(f"\n{'='*60}")
print(f" WARNINGS ({len(issues['WARNING'])} issues)")
print(f"{'='*60}")
for i in issues["WARNING"]:
    print(f"  ⚠ {i}")

print(f"\n{'='*60}")
print(f" INFO ({len(issues['INFO'])} notices)")
print(f"{'='*60}")
for i in issues["INFO"]:
    print(f"  ℹ {i}")

print(f"\n{'='*60}")
total = sum(len(v) for v in issues.values())
print(f" TOTAL: {total} issues found")
print(f"{'='*60}")

# Save JSON report
with open("audit_results.json", "w") as f:
    json.dump(issues, f, indent=2)
print("Report saved to: audit_results.json")
