import sqlite3

conn = sqlite3.connect('synapsehr.db')
cursor = conn.cursor()

def run_query(title, query):
    print(f"\n--- {title} ---")
    cursor.execute(query)
    columns = [description[0] for description in cursor.description]
    print(columns)
    for row in cursor.fetchall():
        print(row)

run_query("LEAVE TYPES", "SELECT id, name FROM leave_types")
run_query("LEAVE BALANCES", "SELECT id, leave_type_id, employee_id, available_days, used_days FROM leave_balances LIMIT 5")
run_query("LEAVE REQUESTS", "SELECT id, employee_id, leave_type_id, status FROM leave_requests LIMIT 5")
run_query("USERS", "SELECT id, email, role FROM users LIMIT 3")
run_query("EMPLOYEES", "SELECT id, user_id FROM employees LIMIT 3")

conn.close()
