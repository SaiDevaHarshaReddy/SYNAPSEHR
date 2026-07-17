import sqlite3
import uuid
from datetime import date, timedelta

conn = sqlite3.connect('synapsehr.db')
cursor = conn.cursor()

# Get leave types
cursor.execute("SELECT id, name, days_per_year FROM leave_types")
leave_types = {row[1]: {'id': row[0], 'days': row[2]} for row in cursor.fetchall()}

# Ensure "Usual Leave" exists if not we can just map it to Casual Leave or create one.
# Prompt said "casual, sick usual and annual". They probably meant casual, sick and annual.
target_types = ['Casual Leave', 'Sick Leave', 'Annual Leave']

# Get all employees
cursor.execute("SELECT id, user_id FROM employees")
employees = cursor.fetchall()

# 1. Insert leave balances for all employees
year = 2026
for emp in employees:
    emp_id = emp[0]
    for lt_name in target_types:
        if lt_name in leave_types:
            lt_id = leave_types[lt_name]['id']
            days = leave_types[lt_name]['days']
            
            # Check if balance exists
            cursor.execute("SELECT id FROM leave_balances WHERE employee_id=? AND leave_type_id=? AND year=?", (emp_id, lt_id, year))
            if not cursor.fetchone():
                lb_id = uuid.uuid4().hex
                cursor.execute("""
                    INSERT INTO leave_balances 
                    (id, employee_id, leave_type_id, available_days, used_days, carry_forward_days, year, created_at, updated_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (lb_id, emp_id, lt_id, days, 0, 0, year))

# 2. Insert example leave requests for the admin employee
admin_emp_id = '93293d9fe67e4fe08c7837b9cfa3b807'
casual_id = leave_types['Casual Leave']['id']
sick_id = leave_types['Sick Leave']['id']
annual_id = leave_types['Annual Leave']['id']

examples = [
    (casual_id, 'approved', 'Family event', 5, 5),
    (sick_id, 'rejected', 'Feeling unwell', -2, -1),
    (annual_id, 'pending', 'Vacation', 10, 15)
]

for lt_id, status, reason, start_delta, end_delta in examples:
    # Check if a similar request exists for this employee
    cursor.execute("SELECT id FROM leave_requests WHERE employee_id=? AND leave_type_id=? AND status=?", (admin_emp_id, lt_id, status))
    if not cursor.fetchone():
        req_id = uuid.uuid4().hex
        start_dt = date.today() + timedelta(days=start_delta)
        end_dt = date.today() + timedelta(days=end_delta)
        cursor.execute("""
            INSERT INTO leave_requests
            (id, employee_id, leave_type_id, start_date, end_date, reason, status, is_read, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (req_id, admin_emp_id, lt_id, start_dt.isoformat(), end_dt.isoformat(), reason, status))

conn.commit()
conn.close()
print("Data seeded successfully!")
