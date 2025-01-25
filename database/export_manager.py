import csv
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from .db_handler import logger

class ExportManager:
    def __init__(self, db_path='database/invoices.db'):
        self.db_path = db_path
        
    def export_to_csv(self, invoice_number=None, output_path=None):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            query = "SELECT * FROM Invoices"
            params = ()
            if invoice_number:
                query += " WHERE invoice_number = ?"
                params = (invoice_number,)
                
            df = pd.read_sql_query(query, conn, params=params)
            
            if output_path is None:
                output_path = Path('reports') / f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
            logger.info(f"CSV export saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            raise
        finally:
            conn.close()

    def export_to_excel(self, invoice_number=None, output_path=None):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            query = "SELECT * FROM Invoices"
            params = ()
            if invoice_number:
                query += " WHERE invoice_number = ?"
                params = (invoice_number,)
                
            df = pd.read_sql_query(query, conn, params=params)
            
            if output_path is None:
                output_path = Path('reports') / f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(output_path, index=False, engine='openpyxl')
            logger.info(f"Excel export saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise
        finally:
            conn.close()
