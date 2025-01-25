from database.db_handler import get_db_connection

with get_db_connection() as conn:
    version = conn.execute("SELECT sqlite_version()").fetchone()[0]
    print(f"SQLite Database Version: {version}")
