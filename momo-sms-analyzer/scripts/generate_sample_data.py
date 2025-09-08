#!/usr/bin/env python3
"""
Generate Sample Data for MoMo SMS Analytics

Creates sample transaction data and exports dashboard JSON for testing.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from etl.load_db import DatabaseManager
from etl.config import DASHBOARD_JSON_PATH


def generate_sample_transactions():
    """Generate sample transaction data for testing."""
    
    categories = ['TRANSFER', 'AIRTIME', 'PAYMENT', 'WITHDRAWAL', 'DEPOSIT']
    networks = ['MTN', 'AIRTEL', 'AFRICELL']
    
    transactions = []
    base_date = datetime(2023, 8, 1)
    
    for i in range(150):
        # Generate random transaction
        transaction_date = base_date + timedelta(days=random.randint(0, 90))
        category = random.choice(categories)
        network = random.choice(networks)
        
        # Generate realistic amounts based on category
        if category == 'AIRTIME':
            amount = random.randint(1000, 20000)
        elif category == 'TRANSFER':
            amount = random.randint(5000, 500000)
        elif category == 'WITHDRAWAL':
            amount = random.randint(20000, 200000)
        elif category == 'PAYMENT':
            amount = random.randint(10000, 300000)
        else:  # DEPOSIT
            amount = random.randint(50000, 1000000)
        
        # Determine transaction type
        if category in ['TRANSFER', 'AIRTIME', 'PAYMENT', 'WITHDRAWAL']:
            transaction_type = 'DEBIT'
        elif category == 'DEPOSIT':
            transaction_type = 'CREDIT'
        else:
            transaction_type = 'UNKNOWN'
        
        transaction = {
            'transaction_id': f'tx_{i+1:04d}',
            'amount': float(amount),
            'currency': 'UGX',
            'transaction_date': transaction_date.isoformat(),
            'transaction_type': transaction_type,
            'category': category,
            'sender_phone': f'+25677{random.randint(1000000, 9999999)}',
            'receiver_phone': f'+25670{random.randint(1000000, 9999999)}',
            'sender_network': network,
            'receiver_network': random.choice(networks),
            'description': f'Sample {category.lower()} transaction',
            'balance_before': float(random.randint(50000, 1000000)),
            'balance_after': float(random.randint(50000, 1000000)),
            'fees': float(random.randint(0, 5000)) if category != 'DEPOSIT' else 0,
            'status': 'SUCCESS',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        transactions.append(transaction)
    
    return transactions


def main():
    """Main function to generate sample data and export dashboard JSON."""
    
    print("🔄 Generating sample transaction data...")
    
    # Generate sample transactions
    transactions = generate_sample_transactions()
    print(f"✅ Generated {len(transactions)} sample transactions")
    
    # Initialize database and insert sample data
    print("💾 Storing data in database...")
    db_manager = DatabaseManager()
    loaded_count = db_manager.insert_transactions(transactions)
    print(f"✅ Loaded {loaded_count} transactions to database")
    
    # Export dashboard data
    print("📊 Exporting dashboard data...")
    success = db_manager.export_to_json(DASHBOARD_JSON_PATH)
    
    if success:
        print(f"✅ Dashboard data exported to: {DASHBOARD_JSON_PATH}")
        print("🎉 Sample data generation complete!")
        print("\n📱 You can now view the dashboard at: http://localhost:8000")
        print("🚀 Start the frontend server with: ./scripts/serve_frontend.sh -o")
    else:
        print("❌ Failed to export dashboard data")
        sys.exit(1)


if __name__ == '__main__':
    main()
