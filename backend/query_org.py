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

run_query("USERS", "SELECT id, email, organization_id FROM users")
run_query("EMPLOYEES", "SELECT id, user_id, organization_id FROM employees")

conn.close()
