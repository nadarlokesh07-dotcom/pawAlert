import sqlite3

conn = sqlite3.connect("pawalert.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE animal_reports
ADD COLUMN condition TEXT
""")

conn.commit()
conn.close()

print("condition column added successfully!")