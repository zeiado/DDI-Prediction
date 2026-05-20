import json
import urllib.request
import urllib.error
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "https://ddi-prediction.onrender.com"

print("==========================================================")
print("DDI-Prediction: Live Render Deployment Validation")
print("==========================================================")

def run_test(method, endpoint, payload, description):
    print(f"\n>>> Test: {description}")
    print(f"{method} {BASE_URL}{endpoint}")
    
    url = f"{BASE_URL}{endpoint}"
    
    if method == "GET":
        req = urllib.request.Request(url, method='GET')
    else:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = response.read().decode('utf-8')
            res_json = json.loads(res_data)
            print(f"[OK] Status: {response.status}")
            print(json.dumps(res_json, indent=2, ensure_ascii=False))
            return res_json
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        try:
            print(f"Body: {e.read().decode('utf-8')}")
        except: pass
    except Exception as e:
        print(f"[ERROR] {e}")
    return None

# 1. Health check
run_test("GET", "/health", None, "Health Check")

# 2. Drug search
run_test("GET", "/search-drugs?q=Cyclo", None, "Drug Search")

# 3. Predict interaction
predict = run_test("POST", "/check-interaction", {
    "drug_a": "Cyclosporine",
    "drug_b": "Daptomycin",
    "use_smiles": False
}, "DDI Prediction (Cyclosporine + Daptomycin)")

# 4. AI Chat Summary
if predict and predict.get("success"):
    run_test("POST", "/chat/summary", {
        "interaction_data": predict
    }, "AI Chat Summary")

print("\n==========================================================")
print("Done!")
print("==========================================================")
