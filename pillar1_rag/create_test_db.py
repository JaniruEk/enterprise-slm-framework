import sqlite3
import os

print("Building local test database...")

# Ensure the data directory exists
os.makedirs("../data", exist_ok=True)

# Connect to the SQLite database file (it will be created if it doesn't exist)
conn = sqlite3.connect("../data/enterprise.db")
cursor = conn.cursor()

# Read your existing schema file
with open("../data/enterprise_schema.sql", "r") as f:
    sql_script = f.read()

# Execute the DDL script to physically create the tables
cursor.executescript(sql_script)
conn.commit()
conn.close()

print("Success: ../data/enterprise.db created with full relational constraints!")