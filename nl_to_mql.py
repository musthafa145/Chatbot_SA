from llama_cpp import Llama
from pprint import pformat
from Chatbot_SA.prior_data_builder import build_prior_data  # <-- you expose this function
import sys

# -----------------------------
# CONFIG
# -----------------------------
MODEL_PATH = "airbnb_sql_model_q4.gguf"
CTX_SIZE = 6096

# -----------------------------
# LOAD LLM
# -----------------------------
llm = Llama(
    model_path=MODEL_PATH,
    chat_format="mistral-instruct",
    n_ctx=CTX_SIZE,
    verbose=False,
)

# -----------------------------
# EXPOSED FUNCTION
# -----------------------------
def llm_fix_fn(bad_query: str, error: str) -> str:
    """
    Fixes only the syntax of a MongoDB query using the loaded LLM.
    """
    prompt = f"""
    The following MongoDB query FAILED to execute due to a SYNTAX error.

    Rules:
    - Do NOT generate  explanations.
    - generate ONLY a syntactically aligned valid MongoDB query.

    Broken query:
    {bad_query}
    """
    
    # Use the chat-style API (like convert_nl_to_mql) instead of raw generate()
    fixed_query_result = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=200,
    )
    
    # Extract the fixed query string
    fixed_query = fixed_query_result["choices"][0]["message"]["content"].strip()
    return fixed_query


def convert_nl_to_mql(user_query: str) -> str:
    """
    Convert a natural language query to MongoDB MQL.
    
    Args:
        user_query: The natural language query string
        
    Returns:
        A MongoDB MQL query string
    """
    # 1. Build prior data FIRST (deterministic step)
    prior_data = build_prior_data(user_query)

    # 2. STRICT prompt (user query is referenced, not free text)
    system_prompt = """
You are a MongoDB MQL generator.

Rules:
- You MUST strictly rely on the provided prior data.
- Do NOT assume any fields or collections.
- Generate exactly ONE valid MongoDB MQL query.
- Do NOT explain.
- Do NOT output anything except the query.
"""

    user_prompt = f"""
Convert the following natural language query to MongoDB MQL
by STRICTLY referring to the prior data below.

Natural language query:
<{user_query}>

Prior data (authoritative):
{pformat(prior_data)}

Return ONE MongoDB MQL query only.
"""

    # 3. LLM call
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=200,
    )

    # 4. Return the query
    return response["choices"][0]["message"]["content"].strip()


# -----------------------------
# MAIN
# -----------------------------
def main():
    # 1. Read user query
    user_query = input("Natural language query: ").strip()

    # 2. Call the exposed function
    mql_query = convert_nl_to_mql(user_query)

    # 3. Output the result
    print(mql_query)


if __name__ == "__main__":
    main()
