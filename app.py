#import os
from flask import Flask, render_template, request, jsonify
#from dotenv import load_dotenv

# --- Internal imports ---
from Chatbot_SA.nl_to_mql import convert_nl_to_mql as plan_query, llm_fix_fn
from Chatbot_SA.shell_executor import execute_with_retry 

# --------------------------------------------------
# App & Environment Setup
# --------------------------------------------------
#print("🟡 [BOOT] Loading environment variables")
#load_dotenv()

#MONGO_URI = os.getenv("mongo_url")
# print(f"🟢 [BOOT] mongo_url loaded = {bool(MONGO_URI)}")

# if not MONGO_URI:
#     raise RuntimeError("❌ mongo_url not found in environment")

app = Flask(__name__)

print("🟢 [BOOT] Flask app initialized")

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route("/")
def index():
    print("🟡 [ROUTE] GET /")
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    print("\n================ CHAT REQUEST START ================")

    data = request.get_json(force=True, silent=True)
    print(f"🟡 [REQUEST] Raw payload = {data}")

    if not data or "message" not in data:
        print("🔴 [ERROR] No message in request")
        return jsonify({"reply": "Please send a message."})

    user_message = data["message"].strip()
    print(f"🟢 [INPUT] user_message = {user_message!r}")

    if not user_message:
        print("🔴 [ERROR] Empty user message")
        return jsonify({"reply": "Please type a question."})

    # --------------------------------------------------
    # 1. LLM → MongoDB Shell Query
    # --------------------------------------------------
    print("🟡 [STEP 1] Calling LLM planner")
    
    mql_query = plan_query(user_message)
    
    print("🟢 [LLM OUTPUT] Raw MQL from model:")
    print(mql_query)
    print(f"🟢 [LLM OUTPUT] Type = {type(mql_query)}") 
    
    if not mql_query or not isinstance(mql_query, str):
        print("🔴 [ERROR] LLM returned invalid output")
        return jsonify({"reply": "Model failed to generate a query."})
    
    # --------------------------------------------------
    # 2. Execute via MongoDB Shell (mongosh)
    # --------------------------------------------------
    print("🟡 [STEP 2] Executing query via shell-based executor")

    result = execute_with_retry(mql_query, llm_fix_fn=llm_fix_fn, max_retry=1)


    print("🟡 [EXECUTOR RESULT]")
    print(result)

    if "error" in result:
        print("🔴 [ERROR] Execution failed")
        return jsonify({
            "reply": f"Sorry, I couldn't process that: {result['error']}",
            "mql": mql_query
        })

    # --------------------------------------------------
    # 3. Format response for UI
    # --------------------------------------------------
    print("🟡 [STEP 3] Formatting response for UI")

    reply_text = format_answer(result)

    print("🟢 [RESPONSE] Final reply text:")
    print(reply_text)

    print("================ CHAT REQUEST END =================\n")

    return jsonify({
        "reply": reply_text,
        "mql": mql_query  # Optional: expose for debugging/demo
    })


# --------------------------------------------------
# Response Formatter
# --------------------------------------------------

def format_answer(result: dict) -> str:
    print("🟡 [FORMAT] Formatting executor result")

    docs = result.get("value", [])
    print(f"🟢 [FORMAT] Documents count = {len(docs)}")

    if not docs:
        return "I found no data matching that criteria in the database."

    summaries = []
    for doc in docs[:5]:
        # Join all key-value pairs in the document
        summary = " | ".join(f"{k}: {v}" for k, v in doc.items())
        summaries.append(f"• {summary}")

    response = (
        f"I found {len(docs)} records. Here are the top matches:\n"
        + "\n".join(summaries)
    )

    return response


# --------------------------------------------------
# Entry Point
# --------------------------------------------------
if __name__ == "__main__":
    print("🟢 [BOOT] Starting Flask dev server")
    app.run(debug=True, port=5000)
