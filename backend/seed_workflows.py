import sqlite3
import uuid
import json
from datetime import datetime, timedelta

def seed_workflows():
    conn = sqlite3.connect('synapsehr.db')
    cursor = conn.cursor()

    # Get some employees
    cursor.execute("SELECT id FROM employees LIMIT 5")
    employees = cursor.fetchall()

    if not employees:
        print("No employees found. Cannot seed workflows.")
        return

    # Workflows to insert
    # status: "completed", "pending"
    mock_workflows = [
        {"type": "onboarding", "status": "completed", "days_ago": 10, "duration_days": 2},
        {"type": "onboarding", "status": "completed", "days_ago": 8, "duration_days": 1},
        {"type": "performance_review", "status": "completed", "days_ago": 5, "duration_days": 3},
        {"type": "offboarding", "status": "completed", "days_ago": 15, "duration_days": 4},
        {"type": "onboarding", "status": "pending", "days_ago": 2, "duration_days": None},
        {"type": "performance_review", "status": "pending", "days_ago": 1, "duration_days": None},
        {"type": "onboarding", "status": "completed", "days_ago": 20, "duration_days": 2},
        {"type": "performance_review", "status": "completed", "days_ago": 25, "duration_days": 5},
    ]

    now = datetime.now()

    for idx, wf_data in enumerate(mock_workflows):
        wf_id = uuid.uuid4().hex
        emp_id = employees[idx % len(employees)][0]
        started_at = now - timedelta(days=wf_data["days_ago"])
        
        completed_at = None
        if wf_data["status"] == "completed" and wf_data["duration_days"]:
            completed_at = started_at + timedelta(days=wf_data["duration_days"])

        cursor.execute("""
            INSERT INTO workflows 
            (id, employee_id, workflow_type, status, state, started_at, completed_at, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            wf_id, 
            emp_id, 
            wf_data["type"], 
            wf_data["status"], 
            json.dumps({"step": 2}), 
            started_at.isoformat(), 
            completed_at.isoformat() if completed_at else None, 
            started_at.isoformat(), 
            started_at.isoformat()
        ))

    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(mock_workflows)} workflows.")

if __name__ == "__main__":
    seed_workflows()
