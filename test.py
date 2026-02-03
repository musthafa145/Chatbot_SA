# test_mongo_connection.py
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv  
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("✅ Connection successful")
except PyMongoError as e:
    print(f"❌ Connection failed: {e}")