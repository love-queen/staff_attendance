import sqlite3

# Connect to the database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Create the attendance_merged table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance_merged (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    date TEXT,
    check_in TEXT,
    check_out TEXT
)
''')

# Insert grouped data from 'attendance_records' table 
cursor.execute('''
INSERT INTO attendance_merged (name, department, date, check_in, check_out)
SELECT
    name,
    department,
    DATE(timestamp) as date,
    MAX(CASE WHEN check_type = 'Check In' THEN TIME(timestamp) END),
    MAX(CASE WHEN check_type = 'Check Out' THEN TIME(timestamp) END)
FROM attendance_records
WHERE DATE(timestamp) NOT IN (
    SELECT date FROM attendance_merged
)
GROUP BY name, department, DATE(timestamp)
''')

conn.commit()
conn.close()

print("✅ attendance_merged table updated successfully!")

