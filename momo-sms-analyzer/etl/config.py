"""
ETL Configuration Module

Contains file paths, thresholds, categories, and other configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# File Paths
XML_INPUT_PATH = os.getenv('XML_INPUT_PATH', 'data/raw/momo.xml')
DASHBOARD_JSON_PATH = os.getenv('DASHBOARD_JSON_PATH', 'data/processed/dashboard.json')
ETL_LOG_PATH = os.getenv('ETL_LOG_PATH', 'data/logs/etl.log')
DEAD_LETTER_PATH = os.getenv('DEAD_LETTER_PATH', 'data/logs/dead_letter/')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/db.sqlite3')

# ETL Processing Configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

# Transaction Categories and Rules
TRANSACTION_CATEGORIES = {
    'TRANSFER': ['transfer', 'send', 'sent'],
    'DEPOSIT': ['deposit', 'receive', 'received', 'top up', 'topup'],
    'WITHDRAWAL': ['withdraw', 'withdrawal', 'cash out', 'cashout'],
    'PAYMENT': ['payment', 'pay', 'purchase', 'buy'],
    'AIRTIME': ['airtime', 'credit', 'recharge'],
    'BILL': ['bill', 'utility', 'electricity', 'water'],
    'OTHER': []  # Default fallback category
}

# Amount thresholds for analysis
AMOUNT_THRESHOLDS = {
    'SMALL': 1000,      # UGX 1,000
    'MEDIUM': 50000,    # UGX 50,000
    'LARGE': 500000,    # UGX 500,000
}

# Phone number patterns (Uganda)
PHONE_PATTERNS = {
    'MTN': r'^(\+256|256|0)?(77|78|76)\d{7}$',
    'AIRTEL': r'^(\+256|256|0)?(75|70|74)\d{7}$',
    'AFRICELL': r'^(\+256|256|0)?(79)\d{7}$',
    'UNKNOWN': r'^(\+256|256|0)?\d{9}$'
}

# Database Configuration
DB_TABLES = {
    'transactions': {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'transaction_id': 'TEXT UNIQUE NOT NULL',
        'amount': 'REAL NOT NULL',
        'currency': 'TEXT DEFAULT "UGX"',
        'transaction_date': 'DATETIME NOT NULL',
        'transaction_type': 'TEXT NOT NULL',
        'category': 'TEXT NOT NULL',
        'sender_phone': 'TEXT',
        'receiver_phone': 'TEXT',
        'sender_network': 'TEXT',
        'receiver_network': 'TEXT',
        'description': 'TEXT',
        'balance_before': 'REAL',
        'balance_after': 'REAL',
        'fees': 'REAL DEFAULT 0',
        'status': 'TEXT DEFAULT "SUCCESS"',
        'created_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': ETL_LOG_PATH,
            'formatter': 'detailed'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'etl': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
