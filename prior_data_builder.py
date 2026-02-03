from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from collections import defaultdict
from dotenv import load_dotenv
from pprint import pprint
import os

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set.")

DB_NAME = "sample_analytics"
MODEL_NAME = "all-MiniLM-L6-v2"
SAMPLE_SIZE = 30
MAX_DICT_DEPTH = 2   # safety limit

# -----------------------------
# RECURSIVE TYPE INFERENCE (NEW)
# -----------------------------
def infer_type_schema(value, depth=0, max_depth=MAX_DICT_DEPTH):
    if depth >= max_depth:
        return {"_type": "dict", "_truncated": True}

    if isinstance(value, dict):
        schema = {}
        for k, v in value.items():
            schema[k] = infer_type_schema(v, depth + 1, max_depth)
        return schema

    if isinstance(value, list):
        if value:
            return {"list_of": infer_type_schema(value[0], depth + 1, max_depth)}
        return {"list_of": "unknown"}

    return type(value).__name__

# -----------------------------
# GET FIELDS + TYPES (MODIFIED)
# -----------------------------
def get_collection_schema(db, collection_name):
    fields = {}
    cursor = db[collection_name].find({}, limit=SAMPLE_SIZE)

    for doc in cursor:
        for k, v in doc.items():
            if k == "_id":
                continue

            # If already inferred deeply, skip
            if k in fields and isinstance(fields[k], dict):
                continue

            if isinstance(v, dict):
                fields[k] = infer_type_schema(v)

            elif isinstance(v, list):
                if v:
                    fields[k] = {"list_of": infer_type_schema(v[0])}
                else:
                    fields[k] = {"list_of": "unknown"}

            else:
                fields[k] = type(v).__name__

    return fields

# -----------------------------
# BUILD COLLECTION TEXT
# -----------------------------
def build_collection_text(name, schema):
    return f"{name}: " + ", ".join(schema.keys())

# -----------------------------
# RELATIONSHIP INFERENCE
# -----------------------------
def infer_relationships(db, schemas, sample_size=20):
    print("[LOG] Inferring relationships with data sampling...")
    relationships = []

    for from_col, from_schema in schemas.items():
        for field in from_schema.keys():
            for to_col, to_schema in schemas.items():
                if from_col == to_col:
                    continue

                candidate_fields = [f for f in to_schema.keys() if f == field or f == "_id"]

                for to_field in candidate_fields:
                    from_values = set()
                    for doc in db[from_col].find({field: {"$exists": True}}, limit=sample_size):
                        from_values.add(doc[field])

                    to_values = set()
                    for doc in db[to_col].find({to_field: {"$exists": True}}, limit=sample_size):
                        to_values.add(doc[to_field])

                    if from_values & to_values:
                        confidence = "high"
                    elif from_values:
                        confidence = "medium"
                    else:
                        continue

                    relationships.append({
                        "from_collection": from_col,
                        "field": field,
                        "to_collection": to_col,
                        "to_field": to_field,
                        "confidence": confidence
                    })

    print(f"[LOG] Relationships found: {relationships}")
    return relationships

# -----------------------------
# EXPOSED FUNCTION
# -----------------------------
def build_prior_data(user_question: str) -> dict:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    collection_names = db.list_collection_names()
    if not collection_names:
        raise RuntimeError("No collections found in database")

    schemas = {}
    for col in collection_names:
        schema = get_collection_schema(db, col)
        if schema:
            schemas[col] = schema

    if not schemas:
        raise RuntimeError("No schemas inferred from collections")

    collection_texts = {
        col: build_collection_text(col, schema)
        for col, schema in schemas.items()
    }

    model = SentenceTransformer(MODEL_NAME)
    q_embedding = model.encode([user_question])

    col_names = list(collection_texts.keys())
    col_texts = list(collection_texts.values())
    col_embeddings = model.encode(col_texts)

    scores = cosine_similarity(q_embedding, col_embeddings)[0]
    ranked_collections = sorted(
        zip(col_names, scores),
        key=lambda x: x[1],
        reverse=True
    )

    relationships = infer_relationships(db, schemas)

    allowed_operations = [
        "find", "filter", "project",
        "sort", "limit", "count",
        "group", "aggregate"
    ]

    prior_data = {
        "user_question": user_question,
        "ranked_collections": [
            {"name": name, "score": round(float(score), 3)}
            for name, score in ranked_collections
        ],
        "schemas": schemas,
        "relationships": relationships,
        "allowed_operations": allowed_operations
    }

    print(f"Prior data built: {prior_data}")
    return prior_data

# -----------------------------
# CLI DEBUG
# -----------------------------
if __name__ == "__main__":
    query = input("User question: ").strip()
    data = build_prior_data(query)
    print("\n=== PRIOR DATA (READY FOR LLM) ===")
    pprint(data)
