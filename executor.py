from pymongo.collection import Collection

ALLOWED_INTENTS = {
    "count_customers",
    "list_customers",
}

def execute_plan(plan: dict, customers_col: Collection):
    """
    Executes a validated intent-based plan safely.
    """

    intent = plan.get("intent")

    # --------------------
    # Safety check (redundant but intentional)
    # --------------------
    if intent not in ALLOWED_INTENTS:
        return {"error": "Invalid intent"}

    # --------------------
    # COUNT customers
    # --------------------
    if intent == "count_customers":
        count = customers_col.count_documents({})
        return {
            "type": "count",
            "value": count
        }

    # --------------------
    # LIST customers
    # --------------------
    if intent == "list_customers":
        cursor = customers_col.find(
            {},
            {"name": 1, "_id": 0}
        ).limit(5)

        names = [doc["name"] for doc in cursor]

        return {
            "type": "list",
            "value": names
        }
