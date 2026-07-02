import sqlite3

print("Connecting to local test database...")
conn = sqlite3.connect("../data/enterprise.db")
cursor = conn.cursor()

# Enforce foreign key constraints inside SQLite session
cursor.execute("PRAGMA foreign_keys = ON;")

try:
    print("Populating 'departments'...")
    cursor.executemany("""
        INSERT OR IGNORE INTO departments (dept_id, department_name, location)
        VALUES (?, ?, ?);
    """, [
        (1, "Engineering", "Kandy"),
        (2, "Human Resources", "Colombo"),
        (3, "Finance", "Kandy")
    ])

    print("Populating 'roles'...")
    cursor.executemany("""
        INSERT OR IGNORE INTO roles (role_id, role_title, base_salary)
        VALUES (?, ?, ?);
    """, [
        (1, "Software Engineer", 150000),
        (2, "Data Scientist", 180000),
        (3, "HR Manager", 120000)
    ])

    print("Populating 'employees'...")
    cursor.executemany("""
        INSERT OR IGNORE INTO employees (emp_id, first_name, last_name, department_id, role_id, hire_date)
        VALUES (?, ?, ?, ?, ?, ?);
    """, [
        (101, "Alice", "Perera", 1, 2, "2024-01-15"),
        (102, "Bob", "Silva", 1, 1, "2024-02-20"),
        (103, "Charlie", "Fernando", 2, 3, "2023-11-01")
    ])

    print("Populating 'project_assignments'...")
    cursor.executemany("""
        INSERT OR IGNORE INTO project_assignments (assignment_id, emp_id, project_name, hours_allocated)
        VALUES (?, ?, ?, ?);
    """, [
        (1001, 101, "Alpha Framework", 40),
        (1002, 101, "Morpheus Core", 20),
        (1003, 102, "Alpha Framework", 35)
    ])

    conn.commit()
    print("\n[Database Status]: Success! Mock records written smoothly.")

except sqlite3.Error as e:
    print(f"\n[Database Error]: Failed to populate tables. {e}")
finally:
    conn.close()
    