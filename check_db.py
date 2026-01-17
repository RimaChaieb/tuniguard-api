import sqlite3

conn = sqlite3.connect('instance/tuniguard.db')
cursor = conn.cursor()

# Check User table columns
try:
    cursor.execute("PRAGMA table_info(users);")
    cols = cursor.fetchall()
    print("Users table columns:")
    for col in cols:
        print(f"  {col[1]} - {col[2]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
