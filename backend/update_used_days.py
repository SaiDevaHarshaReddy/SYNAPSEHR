import sqlite3

conn = sqlite3.connect('synapsehr.db')
cursor = conn.cursor()

admin_emp_id = '93293d9fe67e4fe08c7837b9cfa3b807'
year = 2026

cursor.execute("SELECT id FROM leave_types WHERE name='Casual Leave'")
lt_id = cursor.fetchone()[0]

cursor.execute("UPDATE leave_balances SET used_days = 5, available_days = available_days - 5 WHERE employee_id=? AND leave_type_id=? AND year=?", (admin_emp_id, lt_id, year))
conn.commit()
conn.close()
