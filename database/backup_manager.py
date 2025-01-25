import sqlite3
import os
import shutil
from datetime import datetime
from .logger import logger

class BackupManager:
    def __init__(self, db_path='database/invoices.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self, manual=False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_type = 'manual' if manual else 'auto'
        backup_path = os.path.join(self.backup_dir, 
                                 f"invoice_backup_{timestamp}_{backup_type}.db")
        
        try:
            with sqlite3.connect(self.db_path) as src:
                with sqlite3.connect(backup_path) as dst:
                    src.backup(dst)
            logger.info(f"Backup created: {backup_path}")
            return backup_path  # Return actual path string
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return None  # Explicit None instead of False
            
    def restore_backup(self, backup_path):
        if not backup_path or not os.path.exists(str(backup_path)):
            raise ValueError(f"Invalid backup path: {backup_path}")
            
        try:
            with sqlite3.connect(backup_path) as src: 
                with sqlite3.connect(self.db_path) as dst:
                    src.backup(dst)
            logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False

def create_daily_backup():
    manager = BackupManager()
    return manager.create_backup()
