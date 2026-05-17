import ast
files = [
    'noir-vps/ai_router.py',
    'noir-vps/sovereign_orchestrator.py',
    'noir-vps/grand_singularity_cycle.py',
    'noir-vps/apex_evolution.py',
    'noir-vps/security_enhancer.py',
    'noir-ui/web_server.py',
    'noir-vps/brain.py',
    'noir-vps/neural_coder.py'
]
all_ok = True
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            src = fp.read()
        ast.parse(src)
        print(f"  SYNTAX OK: {f}")
    except SyntaxError as e:
        print(f"  SYNTAX ERROR: {f} — L{e.lineno}: {e.msg}")
        all_ok = False
    except Exception as e:
        print(f"  ERROR: {f} — {e}")
        all_ok = False

print()
if all_ok:
    print("ALL FILES SYNTAX OK — Ready for deployment.")
else:
    print("SYNTAX ERRORS FOUND — Fix before deploying.")
