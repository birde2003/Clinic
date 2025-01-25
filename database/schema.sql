-- Database schema for clinic invoices
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS Invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_generated TEXT NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    owner TEXT,
    full_amount_pending REAL NOT NULL,
    payment_collected REAL DEFAULT 0,
    date_of_payment TEXT,
    date_of_last_payment TEXT,
    payment_method TEXT,
    outstanding REAL GENERATED ALWAYS AS (full_amount_pending - payment_collected) VIRTUAL
);

-- Trigger to update outstanding balance after insert
CREATE TRIGGER IF NOT EXISTS update_outstanding_insert
AFTER INSERT ON Invoices
BEGIN
    UPDATE Invoices SET 
        outstanding = NEW.full_amount_pending - NEW.payment_collected
    WHERE id = NEW.id;
END;

-- Trigger to update outstanding balance after update
CREATE TRIGGER IF NOT EXISTS update_outstanding_update
AFTER UPDATE ON Invoices
BEGIN
    UPDATE Invoices SET 
        outstanding = NEW.full_amount_pending - NEW.payment_collected,
        date_of_last_payment = CASE
            WHEN NEW.payment_collected IS NOT NULL THEN DATE('now')
            ELSE date_of_last_payment
        END
    WHERE id = NEW.id;
END;

-- Trigger to update last payment date when payment is collected
CREATE TRIGGER IF NOT EXISTS update_last_payment_date
AFTER UPDATE OF payment_collected ON Invoices
WHEN NEW.payment_collected IS NOT NULL
BEGIN
    UPDATE Invoices SET 
        date_of_last_payment = DATE('now')
    WHERE id = NEW.id;
END;

COMMIT;
