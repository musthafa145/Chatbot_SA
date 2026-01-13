# executor.py

from pymongo.collection import Collection
from bson import ObjectId

def serialize(doc):
    """Convert MongoDB types to JSON-safe types."""
    if isinstance(doc, dict):
        return {k: serialize(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [serialize(v) for v in doc]
    if isinstance(doc, ObjectId):
        return str(doc)
    return doc


def execute_query(plan: dict, collections: dict):
    """
    Execute a safe query plan on MongoDB.

    plan example:
    {
        "collection": "customers",
        "operation": "find",
        "filter": {"active": True},
        "limit": 5
    }
    """

    if "error" in plan:
        return {"error": plan["error"]}

    collection_name = plan.get("collection")
    operation = plan.get("operation")
    query_filter = plan.get("filter", {})
    limit = plan.get("limit", 10)

    # Get MongoDB collection
    collection: Collection = collections.get(collection_name)
    if collection is None:
        return {"error": "Invalid collection"}

    # Execute operation
    if operation == "find":
        docs = list(collection.find(query_filter).limit(limit))
        return serialize(docs)

    if operation == "count":
        count = collection.count_documents(query_filter)
        return {"count": count}

    return {"error": "Invalid operation"}
