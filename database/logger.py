import logging
import os

def configure_logging():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/errors.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('DBHandler')

logger = configure_logging()
