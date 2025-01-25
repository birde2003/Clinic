import sqlite3
import os

def initialize_database():
    # Create database directory if needed
    os.makedirs('database', exist_ok=True)
    print(f"SQLite version: {sqlite3.version}")
    conn = None  # Initialize connection variable
    
    try:
        print("Attempting to connect to database...")
        conn = sqlite3.connect('database/invoices.db')
        print(f"Database connection established (SQLite {conn.execute('SELECT sqlite_version()').fetchone()[0]})")
        cursor = conn.cursor()
        
        # Create Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                id INTEGER PRIMARY KEY,
                date_generated TEXT NOT NULL,
                invoice_number TEXT UNIQUE,
                owner TEXT,
                full_amount_pending REAL,
                payment_collected REAL,
                date_of_payment TEXT,
                date_of_last_payment TEXT,
                payment_method TEXT,
                outstanding REAL GENERATED ALWAYS AS (full_amount_pending - COALESCE(payment_collected, 0)) VIRTUAL,
                CHECK (date_generated IS NULL OR date(date_generated) IS NOT NULL),
                CHECK (payment_collected BETWEEN 0 AND full_amount_pending)
            )
        ''')

        # Create Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Settings (
                id INTEGER PRIMARY KEY,
                currency TEXT DEFAULT 'USD',
                date_format TEXT DEFAULT 'YYYY-MM-DD',
                payment_methods TEXT DEFAULT 'Cash,Card,Bank Transfer,Utab,Cheque,Stripe,Tabby,Tamara'
            )
        ''')

        # Create triggers
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_payment_dates
            AFTER UPDATE OF payment_collected ON Invoices
            WHEN NEW.payment_collected > 0
            BEGIN
                UPDATE Invoices SET
                    date_of_payment = COALESCE(NEW.date_of_payment, datetime('now')),
                    date_of_last_payment = CASE
                        WHEN NEW.payment_collected >= NEW.full_amount_pending THEN datetime('now')
                        ELSE COALESCE(date_of_last_payment, datetime('now'))
                    END
                WHERE id = NEW.id;
            END;
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS validate_payment_amount
            BEFORE UPDATE OF payment_collected ON Invoices
            BEGIN
                SELECT CASE
                    WHEN NEW.payment_collected < 0 THEN
                        RAISE (ABORT, 'Payment amount cannot be negative')
                    WHEN NEW.payment_collected > OLD.full_amount_pending THEN
                        RAISE (ABORT, 'Payment exceeds pending amount')
                END;
            END;
        ''')
        
        conn.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
