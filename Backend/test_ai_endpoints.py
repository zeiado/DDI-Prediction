import json
import urllib.request
import urllib.error
import sys

# Ensure UTF-8 output in Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:5000"

print("==========================================================")
print("🤖 DDI-Prediction: Complete End-to-End Pipeline Validation")
print("==========================================================")

def run_test(endpoint, payload, description):
    print(f"\n🚀 Test: {description}")
    print(f"POST {BASE_URL}{endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode('utf-8')
            res_json = json.loads(res_data)
            print("\n✅ SUCCESS!")
            print(f"Status Code: {response.status}")
            print("Response:")
            print(json.dumps(res_json, indent=2, ensure_ascii=False))
            return res_json
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Response Body: {error_body}")
        except Exception:
            pass
    except Exception as e:
        print(f"\n❌ Error: {e}")
    return None

# --- Step 1: Predict Interaction ---
# Call check-interaction endpoint with two real drugs loaded in the local DB
predict_payload = {
    "drug_a": "Cyclosporine",
    "drug_b": "Daptomycin",
    "use_smiles": False
}

predict_response = run_test("/check-interaction", predict_payload, "Predict DDI using ML DeepDDI Model")

if predict_response and predict_response.get("success"):
    # --- Step 2: Generate AI Chat Summary ---
    # Take the output of the prediction model and use it for the AI summary
    summary_payload = {
        "interaction_data": predict_response
    }
    
    summary_response = run_test("/chat/summary", summary_payload, "Generate Bilingual AI Summary from Prediction")
    
    # --- Step 3: Ask AI Chat Follow-up ---
    # Ask a follow-up question using the summary context
    if summary_response and summary_response.get("success"):
        message_payload = {
            "interaction_data": predict_response,
            "message": "What should I do if my doctor prescribed both to me?",
            "chat_history": [
                {"role": "assistant", "content": summary_response.get("english", "")}
            ]
        }
        run_test("/chat/message", message_payload, "Send Follow-Up Conversational Message")
else:
    print("\n❌ Pipeline stopped: DDI prediction failed.")
