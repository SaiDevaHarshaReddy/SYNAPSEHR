import sqlite3

conn = sqlite3.connect('synapsehr.db')
cursor = conn.cursor()
cursor.execute("SELECT id, leave_type_id, available_days FROM leave_balances WHERE employee_id='93293d9fe67e4fe08c7837b9cfa3b807'")
print("Balances for admin employee:", cursor.fetchall())
conn.close()
