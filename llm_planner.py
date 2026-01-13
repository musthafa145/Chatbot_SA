# llm_planner.py

import subprocess
import json
from llm_prompt import SYSTEM_PROMPT
import re

def sanitize_json(text: str):
    # Remove C-style comment artifacts like \*
    text = text.replace("\\*", "")
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return text
def ensure_json_object(text: str):
    text = text.strip()
    if not text.startswith("{"):
        text = "{\n" + text
    if not text.endswith("}"):
        text = text + "\n}"
    return text
def normalize_llm_output(text: str):
    text = text.strip()

    # Remove markdown escapes
    text = text.replace("\\_", "_")

    # Remove markdown bold
    if text.startswith("**") and text.endswith("**"):
        text = text[2:-2].strip()

    # If output is multi-line key:value pairs, join with commas
    lines = [line.strip().rstrip(",") for line in text.splitlines() if line.strip()]
    text = ", ".join(lines)

    # Ensure JSON object
    if not text.startswith("{"):
        text = "{ " + text
    if not text.endswith("}"):
        text = text + " }"

    return text




def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else None

def plan_query_llm(user_question: str):
    prompt = SYSTEM_PROMPT + f"\nUSER QUESTION:\n{user_question}\n"

    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt,
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    print("\n===== RAW LLM OUTPUT =====")
    print(output)
    print("==========================\n")
    normalized = normalize_llm_output(output)
    try:
        return json.loads(normalized)
    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON"}



