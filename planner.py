# planner.py

def plan_query(user_question: str):
    """
    Convert a simple natural-language question into
    a structured MongoDB query plan.
    """

    q = user_question.lower()

    # Example 1: active customers
    if "active" in q and "customer" in q:
        return {
            "collection": "customers",
            "operation": "find",
            "filter": {
                "$or": [
                    {"active": True},
                    {"active": {"$exists": False}}
                ]
            },
            "limit": 5
        }

    # Example 2: count customers
    if "how many" in q and "customer" in q:
        return {
            "collection": "customers",
            "operation": "count",
            "filter": {}
        }

    # Fallback
    return {
        "error": "Question not supported yet"
    }


