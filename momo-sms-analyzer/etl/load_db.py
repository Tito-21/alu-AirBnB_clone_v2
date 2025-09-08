"""
Database Loading Module

Creates tables and handles upsert operations to SQLite database.
"""

import sqlite3
import logging
import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime

from .config import DATABASE_URL, DB_TABLES, BASE_DIR

# Setup logging
logger = logging.getLogger('etl.load_db')


class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = db_path
        else:
            # Extract path from DATABASE_URL
            db_url = DATABASE_URL.replace('sqlite:///', '')
            self.db_path = BASE_DIR / db_url
            
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._create_tables()
        
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for table_name, columns in DB_TABLES.items():
                    # Build CREATE TABLE statement
                    column_definitions = []
                    for col_name, col_type in columns.items():
                        column_definitions.append(f"{col_name} {col_type}")
                    
                    create_sql = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {', '.join(column_definitions)}
                    )
                    """
                    
                    cursor.execute(create_sql)
                    logger.info(f"Table '{table_name}' created/verified")
                    
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
            
    def insert_transactions(self, transactions: List[Dict]) -> int:
        """
        Insert or update transactions in the database.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Number of transactions successfully inserted/updated
        """
        if not transactions:
            return 0
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                inserted_count = 0
                for transaction in transactions:
                    if self._upsert_transaction(cursor, transaction):
                        inserted_count += 1
                        
                conn.commit()
                logger.info(f"Successfully inserted/updated {inserted_count} transactions")
                return inserted_count
                
        except Exception as e:
            logger.error(f"Error inserting transactions: {e}")
            raise
            
    def _upsert_transaction(self, cursor: sqlite3.Cursor, transaction: Dict) -> bool:
        """
        Insert or update a single transaction.
        
        Args:
            cursor: Database cursor
            transaction: Transaction dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if transaction already exists
            cursor.execute(
                "SELECT id FROM transactions WHERE transaction_id = ?",
                (transaction['transaction_id'],)
            )
            existing = cursor.fetchone()
            
            # Prepare data for insertion
            data = self._prepare_transaction_data(transaction)
            
            if existing:
                # Update existing transaction
                data['updated_at'] = datetime.now().isoformat()
                
                set_clause = ', '.join([f"{k} = ?" for k in data.keys() if k != 'id'])
                values = [v for k, v in data.items() if k != 'id']
                values.append(existing[0])  # Add ID for WHERE clause
                
                update_sql = f"UPDATE transactions SET {set_clause} WHERE id = ?"
                cursor.execute(update_sql, values)
                logger.debug(f"Updated transaction: {transaction['transaction_id']}")
                
            else:
                # Insert new transaction
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                values = list(data.values())
                
                insert_sql = f"INSERT INTO transactions ({columns}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)
                logger.debug(f"Inserted transaction: {transaction['transaction_id']}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error upserting transaction {transaction.get('transaction_id', 'unknown')}: {e}")
            return False
            
    def _prepare_transaction_data(self, transaction: Dict) -> Dict:
        """
        Prepare transaction data for database insertion.
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Dictionary with database-ready data
        """
        # Map transaction fields to database columns
        data = {
            'transaction_id': transaction.get('transaction_id', ''),
            'amount': float(transaction.get('amount', 0)),
            'currency': transaction.get('currency', 'UGX'),
            'transaction_date': transaction.get('transaction_date', datetime.now().isoformat()),
            'transaction_type': transaction.get('transaction_type', 'UNKNOWN'),
            'category': transaction.get('category', 'OTHER'),
            'sender_phone': transaction.get('sender_phone', ''),
            'receiver_phone': transaction.get('receiver_phone', ''),
            'sender_network': transaction.get('sender_network', ''),
            'receiver_network': transaction.get('receiver_network', ''),
            'description': transaction.get('description', ''),
            'balance_before': float(transaction.get('balance_before', 0)) if transaction.get('balance_before') else None,
            'balance_after': float(transaction.get('balance_after', 0)) if transaction.get('balance_after') else None,
            'fees': float(transaction.get('fees', 0)) if transaction.get('fees') else 0,
            'status': transaction.get('status', 'SUCCESS'),
            'created_at': transaction.get('created_at', datetime.now().isoformat())
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
        
    def get_transactions(self, limit: int = None, filters: Dict = None) -> List[Dict]:
        """
        Retrieve transactions from database.
        
        Args:
            limit: Maximum number of transactions to return
            filters: Dictionary of filter conditions
            
        Returns:
            List of transaction dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                cursor = conn.cursor()
                
                # Build query
                query = "SELECT * FROM transactions"
                params = []
                
                if filters:
                    conditions = []
                    for field, value in filters.items():
                        conditions.append(f"{field} = ?")
                        params.append(value)
                    query += " WHERE " + " AND ".join(conditions)
                    
                query += " ORDER BY transaction_date DESC"
                
                if limit:
                    query += f" LIMIT {limit}"
                    
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                transactions = [dict(row) for row in rows]
                logger.info(f"Retrieved {len(transactions)} transactions from database")
                
                return transactions
                
        except Exception as e:
            logger.error(f"Error retrieving transactions: {e}")
            return []
            
    def get_analytics_data(self) -> Dict:
        """
        Get aggregated analytics data from the database.
        
        Returns:
            Dictionary with analytics data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                analytics = {}
                
                # Total transactions and amount
                cursor.execute("SELECT COUNT(*), SUM(amount) FROM transactions")
                total_count, total_amount = cursor.fetchone()
                analytics['total_transactions'] = total_count or 0
                analytics['total_amount'] = total_amount or 0
                
                # Transactions by category
                cursor.execute("""
                    SELECT category, COUNT(*), SUM(amount) 
                    FROM transactions 
                    GROUP BY category 
                    ORDER BY COUNT(*) DESC
                """)
                analytics['by_category'] = [
                    {'category': row[0], 'count': row[1], 'amount': row[2]}
                    for row in cursor.fetchall()
                ]
                
                # Transactions by type
                cursor.execute("""
                    SELECT transaction_type, COUNT(*), SUM(amount) 
                    FROM transactions 
                    GROUP BY transaction_type 
                    ORDER BY COUNT(*) DESC
                """)
                analytics['by_type'] = [
                    {'type': row[0], 'count': row[1], 'amount': row[2]}
                    for row in cursor.fetchall()
                ]
                
                # Transactions by network
                cursor.execute("""
                    SELECT sender_network, COUNT(*), SUM(amount) 
                    FROM transactions 
                    WHERE sender_network != '' 
                    GROUP BY sender_network 
                    ORDER BY COUNT(*) DESC
                """)
                analytics['by_network'] = [
                    {'network': row[0], 'count': row[1], 'amount': row[2]}
                    for row in cursor.fetchall()
                ]
                
                # Monthly trends
                cursor.execute("""
                    SELECT strftime('%Y-%m', transaction_date) as month, 
                           COUNT(*), SUM(amount)
                    FROM transactions 
                    GROUP BY month 
                    ORDER BY month DESC 
                    LIMIT 12
                """)
                analytics['monthly_trends'] = [
                    {'month': row[0], 'count': row[1], 'amount': row[2]}
                    for row in cursor.fetchall()
                ]
                
                logger.info("Generated analytics data from database")
                return analytics
                
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return {}
            
    def export_to_json(self, output_file: str) -> bool:
        """
        Export analytics data to JSON file for frontend consumption.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            analytics_data = self.get_analytics_data()
            
            # Add metadata
            export_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_transactions': analytics_data.get('total_transactions', 0)
                },
                'analytics': analytics_data
            }
            
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
                
            logger.info(f"Exported analytics data to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False


def load_transactions_to_db(transactions: List[Dict], db_path: str = None) -> int:
    """
    Main function to load transactions into database.
    
    Args:
        transactions: List of transaction dictionaries
        db_path: Optional database path override
        
    Returns:
        Number of transactions loaded successfully
    """
    db_manager = DatabaseManager(db_path)
    return db_manager.insert_transactions(transactions)


def export_dashboard_data(output_file: str, db_path: str = None) -> bool:
    """
    Export dashboard data to JSON file.
    
    Args:
        output_file: Path to output JSON file
        db_path: Optional database path override
        
    Returns:
        True if successful, False otherwise
    """
    db_manager = DatabaseManager(db_path)
    return db_manager.export_to_json(output_file)


if __name__ == "__main__":
    # Example usage
    db_manager = DatabaseManager()
    
    # Test data
    test_transactions = [
        {
            'transaction_id': 'test001',
            'amount': 25000,
            'transaction_date': datetime.now().isoformat(),
            'category': 'TRANSFER',
            'transaction_type': 'DEBIT',
            'description': 'Test transaction'
        }
    ]
    
    # Insert test data
    count = db_manager.insert_transactions(test_transactions)
    print(f"Inserted {count} test transactions")
    
    # Generate analytics
    analytics = db_manager.get_analytics_data()
    print(f"Analytics: {analytics}")
