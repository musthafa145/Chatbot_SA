# schema.py

DATABASE_SCHEMA = {
    "sample_analytics": {
        "customers": {
            "description": "Customer profile and membership information",
            "fields": {
                "_id": "Unique customer identifier",
                "name": "Customer full name",
                "username": "Customer username",
                "email": "Customer email address",
                "address": "Customer address",
                "birthdate": "Date of birth",
                "active": "Whether customer is active",
                "accounts": "List of account IDs owned by the customer",
                "tier_and_details": "Membership tiers and benefits"
            },
            "relationships": {
                "accounts": "accounts.account_id"
            }
        },

        "accounts": {
            "description": "Bank account information",
            "fields": {
                "account_id": "Unique account number",
                "limit": "Credit limit",
                "products": "Banking products linked to the account"
            },
            "relationships": {
                "transactions": "transactions.account_id"
            }
        },

        "transactions": {
            "description": "Financial transactions for accounts",
            "fields": {
                "account_id": "Account number",
                "amount": "Transaction amount",
                "date": "Transaction date",
                "symbol": "Stock or transaction symbol",
                "transaction_code": "Transaction type"
            }
        }
    }
}
