# executor of intent.py
from pymongo.collection import Collection

ALLOWED_INTENTS = {
    "count_customers",
    "list_customers"
}



def execute_plan(plan: dict, customers_col: Collection):
    """
    Executes an intent-based plan safely.
    """

    intent = plan.get("intent")

    # --------------------
    # Validate intent
    # --------------------
    if intent not in ALLOWED_INTENTS:
        return {"error": "Query rejected: Invalid intent"}

    # --------------------
    # COUNT customers
    # --------------------
    if intent == "count_customers":
        filters = plan.get("filters", {})
        count = customers_col.count_documents(filters)
        return {"reply": f"Total customers: {count}"}

    # --------------------
    # LIST customers
    # --------------------
    if intent == "list_customers":
        filters = plan.get("filters", {})
        limit = plan.get("limit", 5)

        cursor = customers_col.find(
            filters,
            {"name": 1, "_id": 0}
        ).limit(limit)

        names = [doc["name"] for doc in cursor]

        if not names:
            return {"reply": "No customers found."}

        return {
            "reply": "Here are some customers: " + ", ".join(names)
        }
