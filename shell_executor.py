import subprocess
import json
import tempfile
import os
import shlex
from dotenv import load_dotenv
from Chatbot_SA.nl_to_mql import llm_fix_fn
# --------------------------------------------------
# Environment Setup
# --------------------------------------------------
print("🟡 [SHELL_EXECUTOR] Loading environment variables")
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DEFAULT_DB = os.getenv("mongo_db", "sample_analytics")

if not MONGO_URI:
    raise RuntimeError("❌ mongo_uri not found in environment variables")
print("🟢 [SHELL_EXECUTOR] mongo_uri loaded successfully")
print(f"🟢 [SHELL_EXECUTOR] default DB = {DEFAULT_DB}")


# --------------------------------------------------
# Core Executor (UNCHANGED)
# --------------------------------------------------
def execute_plan(js_mql: str, db_name: str = None):
    print("\n================ SHELL EXECUTOR START ================")
    print(f"🟡 [INPUT] Raw JS MQL received:")
    print(js_mql)

    if not isinstance(js_mql, str):
        return {"error": "Shell executor expects a string query"}

    js_mql = js_mql.strip()
    target_db = db_name or DEFAULT_DB

    # ---------------- SAFETY ----------------
    forbidden_ops = [
        "insert", "update", "delete", "remove", "drop",
        "bulkWrite", "replaceOne", "replaceMany",
        "updateOne", "updateMany"
    ]

    lowered = js_mql.lower()
    for op in forbidden_ops:
        if op in lowered:
            return {"error": f"Write operation '{op}' is not allowed"}

    # ---------------- BUILD SCRIPT ----------------
    shell_script = f"""
    const db = db.getSiblingDB("{target_db}");
    try {{
        const cursor = {js_mql};
        const results = cursor.toArray();
        print(JSON.stringify(results));
    }} catch (e) {{
        print(JSON.stringify({{"__error__": e.toString()}}));
    }}
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as tmp:
        tmp.write(shell_script)
        script_path = tmp.name

    # ---------------- EXECUTE ----------------
    cmd = ["mongosh", MONGO_URI, "--quiet", script_path]

    try:
        completed = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
    finally:
        try:
            os.remove(script_path)
        except Exception:
            pass

    output = completed.stdout.strip()
    if not output:
        return {"error": "No output returned from MongoDB shell"}

    try:
        parsed = json.loads(output)
        if isinstance(parsed, dict) and "__error__" in parsed:
            return {"error": parsed["__error__"]}
        return {"type": "list", "value": parsed}
    except json.JSONDecodeError:
        return {"error": "Failed to parse MongoDB shell output"}


# --------------------------------------------------
# OPTIONAL RETRY WRAPPER (NEW, NON-BREAKING)
# --------------------------------------------------
def execute_with_retry(js_mql: str, llm_fix_fn, db_name: str = None, max_retry: int = 1):
    """
    Executes MQL.
    If MongoDB rejects due to syntax/runtime error,
    asks LLM to FIX SYNTAX ONLY and retries.

    llm_fix_fn: function(bad_query: str, error: str) -> corrected_query
    """
    print("\n================ RETRY EXECUTOR START ================")
    print(f"🟡 [INPUT] Original query:\n{js_mql}")
    print(f"🟡 [INFO] Max retry = {max_retry}")

    result = execute_plan(js_mql, db_name)
    print(f"🟡 [STEP 1] Result from execute_plan: {result}")

    if "error" not in result:
        print("🟢 [INFO] Query executed successfully on first attempt")
        return result

    error_msg = result.get("error", "")
    print(f"🔴 [WARNING] Query failed with error: {error_msg}")

    if max_retry <= 0:
        print("🟡 [INFO] No retries left, returning original error")
        return result

    # 🔁 Ask LLM ONLY to correct syntax
    print("🟡 [STEP 2] Asking LLM to fix syntax only")
    corrected_query = llm_fix_fn(
        bad_query=js_mql,
        error=error_msg
    )
    print(f"🟡 [STEP 2] Corrected query from LLM:\n{corrected_query}")

    if not corrected_query:
        print("🔴 [ERROR] LLM returned empty query, aborting retry")
        return result

    if corrected_query == js_mql:
        print("🔴 [ERROR] LLM returned same query as input, aborting retry")
        return result

    print("🟡 [STEP 3] Retrying execution with corrected query")
    retry_result = execute_plan(corrected_query, db_name)
    print(f"🟡 [STEP 3] Result from retry: {retry_result}")

    if "error" not in retry_result:
        print("🟢 [INFO] Query executed successfully after LLM correction")
    else:
        print("🔴 [ERROR] Retry failed, returning final error")

    print("================ RETRY EXECUTOR END =================\n")
    return retry_result
