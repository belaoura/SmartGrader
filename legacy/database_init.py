import sqlite3
import os

def initialize_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "smart_grader.db")
    schema_path = os.path.join(base_dir, "schema.sql")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    initialize_database()
