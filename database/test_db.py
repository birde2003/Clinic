import pytest
from datetime import datetime
from database.db_handler import get_db_connection, DatabaseError

def test_valid_invoice_workflow():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Test valid workflow
        # Cleanup any existing test data
        cursor.execute("DELETE FROM Invoices WHERE invoice_number LIKE 'INV-%'")
            
        valid_data = {
            'date_generated': datetime.now().isoformat(),
            'invoice_number': 'INV-001',
            'owner': 'John Doe',
            'full_amount_pending': 1000.0,
            'payment_collected': 0.0
        }
        
        # Test insert
        cursor.execute('''
            INSERT INTO Invoices (
                date_generated, invoice_number, owner,
                full_amount_pending, payment_collected
            ) VALUES (?, ?, ?, ?, ?)
        ''', tuple(valid_data.values()))
        
        # Test update
        cursor.execute('''
            UPDATE Invoices 
            SET payment_collected = 500.0 
            WHERE invoice_number = 'INV-001'
        ''')
        
        # Verify calculations
        cursor.execute('''
            SELECT outstanding, date_of_last_payment 
            FROM Invoices 
            WHERE invoice_number = 'INV-001'
        ''')
        result = cursor.fetchone()
        assert result['outstanding'] == 500.0
        assert result['date_of_last_payment'] is not None

def test_invalid_scenarios():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Test duplicate invoice number
        with pytest.raises(DatabaseError, match=r"UNIQUE constraint failed: Invoices.invoice_number"):
            cursor.execute('''
                INSERT INTO Invoices (invoice_number, date_generated, full_amount_pending)
                VALUES (?, ?, ?)
            ''', ('INV-001', datetime.now().isoformat(), 1000.0))
            
        # Test invalid amount type
        with pytest.raises(DatabaseError, match="Full amount must be numeric"):
            cursor.execute('''
                INSERT INTO Invoices (invoice_number, date_generated, full_amount_pending)
                VALUES ('INV-002', datetime('now'), 'one thousand')
            ''')
            
        # Test invalid date format
        with pytest.raises(DatabaseError, match="Invalid isoformat"):
            cursor.execute('''
                INSERT INTO Invoices (invoice_number, date_generated, full_amount_pending)
                VALUES ('INV-003', '2023-13-32', 1000.0)
            ''')

if __name__ == "__main__":
    test_valid_invoice_workflow()
    test_invalid_scenarios()
    print("All tests passed successfully")
