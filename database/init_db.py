import sqlite3
import sys

def init_database():
    try:
        conn = sqlite3.connect('database/invoices.db')
        with open('database/schema.sql', 'r') as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()
        print("Database initialized successfully")
        return True
    except sqlite3.Error as e:
        print(f"SQLite error: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Schema file not found", file=sys.stderr)
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if init_database():
        sys.exit(0)
    else:
        sys.exit(1)
