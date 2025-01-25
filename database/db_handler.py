import sqlite3
import logging
from typing import Optional

class DBHandler:
    def __init__(self, db_path: str = 'database/invoices.db'):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        logging.basicConfig(
            filename='database/db_errors.log',
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def __enter__(self):
        self.connect()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self._enable_foreign_keys()
        except sqlite3.Error as e:
            logging.error(f"Connection error: {str(e)}")
            raise

    def _enable_foreign_keys(self):
        if self.connection:
            self.connection.execute("PRAGMA foreign_keys = ON")

    def execute_query(self, query: str, params: tuple = ()):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor
        except sqlite3.Error as e:
            logging.error(f"Query error: {str(e)}\nQuery: {query}\nParams: {params}")
            raise

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                logging.error(f"Closing error: {str(e)}")
            finally:
                self.connection = None

def get_db_connection():
    """Create and return a new DBHandler instance"""
    return DBHandler()

def validate_db_schema(connection: sqlite3.Connection):
    """Validate core database schema exists"""
    required_tables = {'Invoices'}
    required_triggers = {
        'update_outstanding_insert',
        'update_outstanding_update', 
        'update_last_payment_date'
    }
    
    tables = {row[0] for row in 
        connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    triggers = {row[0] for row in 
        connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}

    missing_tables = required_tables - tables
    missing_triggers = required_triggers - triggers
    
    if missing_tables:
        raise RuntimeError(f"Missing tables: {', '.join(missing_tables)}")
    if missing_triggers:
        raise RuntimeError(f"Missing triggers: {', '.join(missing_triggers)}")
