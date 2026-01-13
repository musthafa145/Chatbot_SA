from flask import Flask, request

# Simulated local database
local_db = {
    "employees": [
        {"id": 1, "name": "Alice", "role": "Engineer"},
        {"id": 2, "name": "Bob", "role": "Manager"},
        {"id": 3, "name": "Charlie", "role": "Analyst"}
    ]
}

def register_routes(app):

    
    @app.route('/db-query', methods=['POST'])
    def db_query():
        query = request.json.get("query", "").lower()
        if not query:
            return {"reply": "Please type a query"}

        # Example: simple keyword-based search
        if "employee" in query:
            names = [e["name"] for e in local_db["employees"]]
            return {"reply": "Employees: " + ", ".join(names)}

        return {"reply": "No data found for your query"}
