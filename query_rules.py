# query_rules.py

ALLOWED_OPERATIONS = {
    "customers": ["find", "count"],
    "accounts": ["find"],
    "transactions": ["find"]
}

ALLOWED_FIELDS = {
    "customers": [
        "username", "name", "email", "birthdate",
        "active", "accounts", "tier_and_details"
    ],
    "accounts": [
        "account_id", "limit", "products"
    ],
    "transactions": [
        "account_id", "transaction_count",
        "bucket_start_date", "bucket_end_date",
        "transactions"
    ]
}





