from database.connection import return_db

try:
    db = return_db()
    print(f"connected to {db.name}")

except Exception as e:
    print(e)

