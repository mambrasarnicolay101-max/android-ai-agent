#!/usr/bin/env python3
"""Tes diagnostik dependency Grand Evolution Loop."""
import sys, traceback, json
sys.path.insert(0, 'noir-vps')

results = {}

# 1) ai_router
print("=== TEST 1: ai_router ===")
try:
    from ai_router import OmniRouter
    r = OmniRouter()
    results['ai_router'] = 'loaded'
    resp = r.query("Respond with one word: OPERATIONAL", task_type="reasoning")
    results['ai_router_response'] = resp[:200]
    print("OK:", resp[:200])
except Exception:
    results['ai_router'] = 'FAIL'
    traceback.print_exc()

# 2) vector_memory
print("\n=== TEST 2: vector_memory ===")
try:
    import vector_memory
    results['vector_memory'] = 'loaded'
    print("OK")
except Exception as e:
    results['vector_memory'] = f'FAIL: {e}'
    print("FAIL:", e)

# 3) evolution_engine
print("\n=== TEST 3: evolution_engine ===")
try:
    import evolution_engine
    results['evolution_engine'] = 'loaded'
    print("OK")
except Exception as e:
    results['evolution_engine'] = f'FAIL: {e}'
    print("FAIL:", e)

# 4) noir_meta_judge
print("\n=== TEST 4: noir_meta_judge ===")
try:
    from noir_meta_judge import NoirMetaJudge
    j = NoirMetaJudge()
    r1 = j.score_ops1("flask api login sqlite react", "import flask\ntry: conn=True\nexcept: pass\n@app.route('/login')\ndef login(): pass\n# test_login\ndef test_login(): pass\n# README example")
    print(f"Ops1 Score: {r1['score']}/100")
    results['meta_judge'] = f"OK - Ops1={r1['score']}"
except Exception as e:
    results['meta_judge'] = f'FAIL: {e}'
    traceback.print_exc()

# 5) noir_external_injector
print("\n=== TEST 5: noir_external_injector ===")
try:
    from noir_external_injector import NoirExternalInjector
    inj = NoirExternalInjector()
    cves = inj.fetch_critical_cves(days=7, max_count=2)
    print(f"CVEs: {len(cves)} fetched")
    for c in cves:
        print(f"  {c.get('id')} CVSS={c.get('cvss')}")
    results['external_injector'] = f'OK - {len(cves)} CVEs'
except Exception as e:
    results['external_injector'] = f'FAIL: {e}'
    print("FAIL:", e)

# 6) Grand Evolution Loop import
print("\n=== TEST 6: Grand Evolution Loop ===")
try:
    from noir_grand_evolution_loop import GrandEvolutionLoop
    loop = GrandEvolutionLoop()
    status = loop.get_status()
    print("OK:", json.dumps(status, indent=2))
    results['grand_loop'] = 'loaded'
except Exception as e:
    results['grand_loop'] = f'FAIL: {e}'
    traceback.print_exc()

print("\n=== RESULTS ===")
for k, v in results.items():
    status = "OK" if not v.startswith("FAIL") else "FAIL"
    print(f"  [{status}] {k}: {str(v)[:100]}")
