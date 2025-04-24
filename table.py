import sqlite3
# Connect to your SQLite database
conn = sqlite3.connect("todosapp.db")
cursor = conn.cursor()

# Table name to clear
table_name = "todos"

# Delete all rows from the table
cursor.execute(f"DROP TABLE {table_name}")  # Changed from TRUNCATE to DELETE FROM

conn.commit()
conn.close()