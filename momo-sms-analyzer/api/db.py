"""
Database Connection Helper for API

Provides database access methods for the FastAPI application.
"""

import sys
from pathlib import Path

# Add parent directory to path to import ETL modules
sys.path.append(str(Path(__file__).parent.parent))

from etl.load_db import DatabaseManager as ETLDatabaseManager


class DatabaseManager(ETLDatabaseManager):
    """
    API Database Manager extending the ETL DatabaseManager.
    
    Provides additional methods specific to API requirements.
    """
    
    def __init__(self, db_path: str = None):
        super().__init__(db_path)
    
    def get_transactions_count(self, filters: dict = None) -> int:
        """
        Get total count of transactions (for pagination).
        
        Args:
            filters: Optional filter conditions
            
        Returns:
            Total number of transactions matching filters
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT COUNT(*) FROM transactions"
                params = []
                
                if filters:
                    conditions = []
                    for field, value in filters.items():
                        conditions.append(f"{field} = ?")
                        params.append(value)
                    query += " WHERE " + " AND ".join(conditions)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                return result[0] if result else 0
                
        except Exception as e:
            self.logger.error(f"Error getting transaction count: {e}")
            return 0
    
    def get_connection(self):
        """Get database connection (for context manager use)."""
        import sqlite3
        return sqlite3.connect(self.db_path)
