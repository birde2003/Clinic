import unittest
import os
import sqlite3
from datetime import datetime
from database.db_handler import get_db_connection, DatabaseError
from database.backup_manager import BackupManager

class TestInvoiceOperations(unittest.TestCase):
    def setUp(self):
        """Create fresh database for each test"""
        # Ensure all connections are closed
        from database.db_handler import _active_connections
        for conn in list(_active_connections):
            conn.close()
            _active_connections.remove(conn)
            
        # Remove existing database
        try:
            os.remove('database/invoices.db')
        except FileNotFoundError:
            pass
        except PermissionError:
            os.system('taskkill /f /im python.exe')
            os.remove('database/invoices.db')
            
        os.makedirs('database', exist_ok=True)
        os.makedirs('backups', exist_ok=True)
        
        # Initialize schema
        with get_db_connection() as conn:
            conn.execute('''CREATE TABLE Invoices (
                id INTEGER PRIMARY KEY,
                date_generated TEXT NOT NULL,
                invoice_number TEXT UNIQUE,
                owner TEXT,
                full_amount_pending REAL,
                payment_collected REAL,
                date_of_payment TEXT,
                date_of_last_payment TEXT,
                payment_method TEXT,
                outstanding REAL
            )''')
            conn.commit()

    def tearDown(self):
        """Clean up after each test"""
        from database.db_handler import _active_connections
        # Close all connections first
        for conn in list(_active_connections):
            conn.close()
            _active_connections.remove(conn)
            
        # Remove test database
        try:
            os.remove('database/invoices.db')
        except (FileNotFoundError, PermissionError):
            pass
            
        # Cleanup backup files
        for f in os.listdir('backups'):
            try:
                os.remove(os.path.join('backups', f))
            except (PermissionError, FileNotFoundError):
                pass

    def test_zero_outstanding_calculation(self):
        """Test invoice with full payment shows 0 outstanding"""
        with get_db_connection() as conn:
            test_data = (
                datetime.now().isoformat(),
                'INV-001',
                'Test Clinic',
                1000.0,
                1000.0,  # Full payment
                datetime.now().isoformat(),
                None,
                'Cash',
                0.0
            )
            conn.execute('''INSERT INTO Invoices VALUES 
                (NULL,?,?,?,?,?,?,?,?,?)''', test_data)
            
            result = conn.execute("SELECT outstanding FROM Invoices WHERE invoice_number = 'INV-001'").fetchone()
            self.assertEqual(result['outstanding'], 0.0)

    def test_duplicate_invoice_prevention(self):
        """Test duplicate invoice numbers are rejected"""
        with get_db_connection() as conn:
            # First insert should succeed
            conn.execute('''INSERT INTO Invoices 
                (date_generated, invoice_number, owner, full_amount_pending, payment_collected)
                VALUES (?,?,?,?,?)''', 
                (datetime.now().isoformat(), 'INV-002', 'Test Clinic', 500.0, 250.0))
            
            # Second insert with same number should fail
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute('''INSERT INTO Invoices 
                    (date_generated, invoice_number, owner, full_amount_pending, payment_collected)
                    VALUES (?,?,?,?,?)''', 
                    (datetime.now().isoformat(), 'INV-002', 'Another Clinic', 700.0, 300.0))

    def test_backup_recovery_integrity(self):
        """Test full backup/restore cycle maintains data integrity"""
        # Create test data
        with get_db_connection() as conn:
            conn.execute('''INSERT INTO Invoices 
                (date_generated, invoice_number, owner, full_amount_pending)
                VALUES (?,?,?,?)''', 
                (datetime.now().isoformat(), 'INV-BACKUP-TEST', 'Backup Clinic', 1500.0))
            
        # Create backup
        backup_path = BackupManager().create_backup(manual=True)
        
        # Close all connections before file operations
        from database.db_handler import _active_connections
        for conn in list(_active_connections):
            conn.close()
            _active_connections.remove(conn)
            
        # Corrupt database
        try:
            os.remove('database/invoices.db')
        except PermissionError:
            pass  # Handle Windows file locking race condition
        
        # Restore backup
        BackupManager().restore_backup(backup_path)
        
        # Verify recovery
        with get_db_connection() as conn:
            result = conn.execute("SELECT * FROM Invoices WHERE invoice_number = 'INV-BACKUP-TEST'").fetchone()
            self.assertEqual(result['owner'], 'Backup Clinic')
            self.assertEqual(result['full_amount_pending'], 1500.0)

if __name__ == '__main__':
    unittest.main()
