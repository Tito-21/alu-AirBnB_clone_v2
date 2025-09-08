"""
Transaction Categorization Module

Simple rules for categorizing MoMo SMS transactions into different types.
"""

import re
import logging
from typing import Dict, List

from .config import TRANSACTION_CATEGORIES, AMOUNT_THRESHOLDS

# Setup logging
logger = logging.getLogger('etl.categorize')


class TransactionCategorizer:
    """Transaction categorization utilities."""
    
    def __init__(self):
        self.categories = TRANSACTION_CATEGORIES
        self.amount_thresholds = AMOUNT_THRESHOLDS
        
    def categorize_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize a list of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of transactions with added categorization fields
        """
        categorized_transactions = []
        
        for transaction in transactions:
            categorized = self.categorize_transaction(transaction)
            categorized_transactions.append(categorized)
            
        logger.info(f"Categorized {len(categorized_transactions)} transactions")
        return categorized_transactions
        
    def categorize_transaction(self, transaction: Dict) -> Dict:
        """
        Categorize a single transaction based on description and other fields.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Transaction with added category and other classification fields
        """
        categorized = transaction.copy()
        
        # Primary categorization based on description/body
        category = self._categorize_by_description(transaction.get('description', ''))
        if not category:
            category = self._categorize_by_body(transaction.get('raw_body', ''))
        if not category:
            category = 'OTHER'
            
        categorized['category'] = category
        
        # Transaction type inference
        transaction_type = self._infer_transaction_type(transaction, category)
        categorized['transaction_type'] = transaction_type
        
        # Amount categorization
        amount_category = self._categorize_by_amount(transaction.get('amount', 0))
        categorized['amount_category'] = amount_category
        
        # Time-based categorization
        time_category = self._categorize_by_time(transaction.get('transaction_date', ''))
        categorized['time_category'] = time_category
        
        return categorized
        
    def _categorize_by_description(self, description: str) -> str:
        """
        Categorize transaction based on description text.
        
        Args:
            description: Transaction description
            
        Returns:
            Category name or empty string if no match
        """
        if not description:
            return ''
            
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.categories.items():
            if category == 'OTHER':
                continue
                
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    logger.debug(f"Categorized as {category} based on keyword: {keyword}")
                    return category
                    
        return ''
        
    def _categorize_by_body(self, body: str) -> str:
        """
        Categorize transaction based on SMS body text.
        
        Args:
            body: Raw SMS body text
            
        Returns:
            Category name or empty string if no match
        """
        if not body:
            return ''
            
        body_lower = body.lower()
        
        # Common MoMo SMS patterns
        if 'you have sent' in body_lower or 'sent to' in body_lower:
            return 'TRANSFER'
        elif 'you have received' in body_lower or 'received from' in body_lower:
            return 'DEPOSIT'
        elif 'cash out' in body_lower or 'withdrawal' in body_lower:
            return 'WITHDRAWAL'
        elif 'airtime' in body_lower or 'top up' in body_lower:
            return 'AIRTIME'
        elif 'payment' in body_lower or 'paid to' in body_lower:
            return 'PAYMENT'
        elif 'bill' in body_lower or 'utility' in body_lower:
            return 'BILL'
            
        return ''
        
    def _infer_transaction_type(self, transaction: Dict, category: str) -> str:
        """
        Infer transaction type (DEBIT/CREDIT) based on category and other fields.
        
        Args:
            transaction: Transaction dictionary
            category: Already determined category
            
        Returns:
            Transaction type (DEBIT, CREDIT, or UNKNOWN)
        """
        # Rules based on category
        if category in ['TRANSFER', 'WITHDRAWAL', 'PAYMENT', 'AIRTIME', 'BILL']:
            return 'DEBIT'
        elif category == 'DEPOSIT':
            return 'CREDIT'
            
        # Try to infer from balance changes
        balance_before = transaction.get('balance_before', 0)
        balance_after = transaction.get('balance_after', 0)
        
        if balance_before and balance_after:
            if balance_after > balance_before:
                return 'CREDIT'
            elif balance_after < balance_before:
                return 'DEBIT'
                
        # Try to infer from SMS body patterns
        body = transaction.get('raw_body', '').lower()
        if any(phrase in body for phrase in ['sent', 'paid', 'withdraw', 'cash out']):
            return 'DEBIT'
        elif any(phrase in body for phrase in ['received', 'deposit', 'credited']):
            return 'CREDIT'
            
        return 'UNKNOWN'
        
    def _categorize_by_amount(self, amount: float) -> str:
        """
        Categorize transaction based on amount thresholds.
        
        Args:
            amount: Transaction amount
            
        Returns:
            Amount category (SMALL, MEDIUM, LARGE, VERY_LARGE)
        """
        if amount <= self.amount_thresholds['SMALL']:
            return 'SMALL'
        elif amount <= self.amount_thresholds['MEDIUM']:
            return 'MEDIUM'
        elif amount <= self.amount_thresholds['LARGE']:
            return 'LARGE'
        else:
            return 'VERY_LARGE'
            
    def _categorize_by_time(self, transaction_date: str) -> str:
        """
        Categorize transaction based on time of day.
        
        Args:
            transaction_date: ISO format datetime string
            
        Returns:
            Time category (MORNING, AFTERNOON, EVENING, NIGHT)
        """
        if not transaction_date:
            return 'UNKNOWN'
            
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(transaction_date.replace('Z', '+00:00'))
            hour = dt.hour
            
            if 5 <= hour < 12:
                return 'MORNING'
            elif 12 <= hour < 17:
                return 'AFTERNOON'
            elif 17 <= hour < 21:
                return 'EVENING'
            else:
                return 'NIGHT'
                
        except Exception as e:
            logger.warning(f"Could not parse date for time categorization: {e}")
            return 'UNKNOWN'
            
    def get_category_statistics(self, transactions: List[Dict]) -> Dict:
        """
        Get statistics about transaction categories.
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dictionary with category statistics
        """
        stats = {
            'total_transactions': len(transactions),
            'categories': {},
            'transaction_types': {},
            'amount_categories': {},
            'time_categories': {}
        }
        
        for transaction in transactions:
            # Category stats
            category = transaction.get('category', 'UNKNOWN')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Transaction type stats
            tx_type = transaction.get('transaction_type', 'UNKNOWN')
            stats['transaction_types'][tx_type] = stats['transaction_types'].get(tx_type, 0) + 1
            
            # Amount category stats
            amount_cat = transaction.get('amount_category', 'UNKNOWN')
            stats['amount_categories'][amount_cat] = stats['amount_categories'].get(amount_cat, 0) + 1
            
            # Time category stats
            time_cat = transaction.get('time_category', 'UNKNOWN')
            stats['time_categories'][time_cat] = stats['time_categories'].get(time_cat, 0) + 1
            
        return stats


def categorize_transactions(transactions: List[Dict]) -> List[Dict]:
    """
    Main function to categorize transactions.
    
    Args:
        transactions: List of cleaned transaction dictionaries
        
    Returns:
        List of categorized transactions
    """
    categorizer = TransactionCategorizer()
    return categorizer.categorize_transactions(transactions)


def get_transaction_insights(transactions: List[Dict]) -> Dict:
    """
    Get insights and statistics from categorized transactions.
    
    Args:
        transactions: List of categorized transactions
        
    Returns:
        Dictionary with insights and statistics
    """
    categorizer = TransactionCategorizer()
    stats = categorizer.get_category_statistics(transactions)
    
    # Add additional insights
    insights = {
        'statistics': stats,
        'insights': {
            'most_common_category': max(stats['categories'], key=stats['categories'].get) if stats['categories'] else 'None',
            'most_common_time': max(stats['time_categories'], key=stats['time_categories'].get) if stats['time_categories'] else 'None',
            'debit_credit_ratio': stats['transaction_types'].get('DEBIT', 0) / max(stats['transaction_types'].get('CREDIT', 1), 1)
        }
    }
    
    return insights


if __name__ == "__main__":
    # Example usage
    sample_transactions = [
        {
            'transaction_id': 'tx001',
            'amount': 50000,
            'description': 'Payment for goods',
            'raw_body': 'You have sent UGX 50,000 to John Doe',
            'transaction_date': '2023-10-15T14:30:00'
        },
        {
            'transaction_id': 'tx002',
            'amount': 10000,
            'description': 'Airtime purchase',
            'raw_body': 'You have bought UGX 10,000 airtime',
            'transaction_date': '2023-10-15T08:15:00'
        }
    ]
    
    categorized = categorize_transactions(sample_transactions)
    insights = get_transaction_insights(categorized)
    
    print("Categorized transactions:")
    for t in categorized:
        print(f"  {t['transaction_id']}: {t['category']} ({t['transaction_type']})")
        
    print(f"\nInsights: {insights['insights']}")
