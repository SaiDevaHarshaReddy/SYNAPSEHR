import sqlite3

conn = sqlite3.connect('synapsehr.db')
cursor = conn.cursor()
cursor.execute("SELECT id, first_name, last_name, user_id FROM employees WHERE user_id='79eedd5ed65c46debbfdfac0fa52ac2b' OR user_id='79eedd5e-d65c-46de-bbfd-fac0fa52ac2b'")
print(cursor.fetchall())
conn.close()
