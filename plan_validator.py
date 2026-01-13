ALLOWED_INTENTS = {
    "list_customers",
    "count_customers",
}

def validate_plan(plan: dict):
    if not isinstance(plan, dict):
        return False, "Plan is not a JSON object"

    intent = plan.get("intent")

    if intent not in ALLOWED_INTENTS:
        return False, "Invalid intent"

    return True, None
