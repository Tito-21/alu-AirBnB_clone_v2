"""
Data Cleaning and Normalization Module

Handles cleaning and normalization of amounts, dates, phone numbers, and other transaction data.
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dateutil import parser as date_parser

from .config import PHONE_PATTERNS

# Setup logging
logger = logging.getLogger('etl.clean_normalize')


class DataCleaner:
    """Data cleaning and normalization utilities."""
    
    def __init__(self):
        self.phone_patterns = PHONE_PATTERNS
        
    def clean_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Clean and normalize a list of transactions.
        
        Args:
            transactions: List of raw transaction dictionaries
            
        Returns:
            List of cleaned transaction dictionaries
        """
        cleaned_transactions = []
        
        for transaction in transactions:
            try:
                cleaned_transaction = self.clean_transaction(transaction)
                if cleaned_transaction:
                    cleaned_transactions.append(cleaned_transaction)
            except Exception as e:
                logger.warning(f"Failed to clean transaction: {e}")
                continue
                
        logger.info(f"Cleaned {len(cleaned_transactions)} out of {len(transactions)} transactions")
        return cleaned_transactions
        
    def clean_transaction(self, transaction: Dict) -> Optional[Dict]:
        """
        Clean and normalize a single transaction.
        
        Args:
            transaction: Raw transaction dictionary
            
        Returns:
            Cleaned transaction dictionary or None if cleaning fails
        """
        try:
            cleaned = transaction.copy()
            
            # Clean and normalize phone numbers
            if 'sender_phone' in transaction:
                cleaned['sender_phone'] = self.normalize_phone_number(transaction['sender_phone'])
                cleaned['sender_network'] = self.identify_network(cleaned['sender_phone'])
                
            if 'receiver_phone' in transaction:
                cleaned['receiver_phone'] = self.normalize_phone_number(transaction['receiver_phone'])
                cleaned['receiver_network'] = self.identify_network(cleaned['receiver_phone'])
                
            # Clean and normalize amounts
            if 'amount' in transaction:
                cleaned['amount'] = self.normalize_amount(transaction['amount'])
                
            if 'balance_before' in transaction:
                cleaned['balance_before'] = self.normalize_amount(transaction['balance_before'])
                
            if 'balance_after' in transaction:
                cleaned['balance_after'] = self.normalize_amount(transaction['balance_after'])
                
            if 'fees' in transaction:
                cleaned['fees'] = self.normalize_amount(transaction['fees'])
                
            # Clean and normalize dates
            if 'transaction_date' in transaction:
                cleaned['transaction_date'] = self.normalize_date(transaction['transaction_date'])
                
            # Clean text fields
            if 'description' in transaction:
                cleaned['description'] = self.clean_text(transaction['description'])
                
            # Generate transaction ID if not present
            if 'transaction_id' not in cleaned or not cleaned['transaction_id']:
                cleaned['transaction_id'] = self.generate_transaction_id(cleaned)
                
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning transaction: {e}")
            return None
            
    def normalize_phone_number(self, phone: str) -> str:
        """
        Normalize phone number to standard format.
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Normalized phone number
        """
        if not phone or not isinstance(phone, str):
            return ''
            
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if phone.startswith('256'):
            return '+' + phone
        elif phone.startswith('0') and len(phone) == 10:
            return '+256' + phone[1:]
        elif len(phone) == 9:
            return '+256' + phone
        else:
            return phone  # Return as-is if format is unclear
            
    def identify_network(self, phone: str) -> str:
        """
        Identify network provider based on phone number.
        
        Args:
            phone: Normalized phone number
            
        Returns:
            Network provider name
        """
        if not phone:
            return 'UNKNOWN'
            
        for network, pattern in self.phone_patterns.items():
            if re.match(pattern, phone):
                return network
                
        return 'UNKNOWN'
        
    def normalize_amount(self, amount) -> float:
        """
        Normalize amount to float value.
        
        Args:
            amount: Raw amount (string, int, or float)
            
        Returns:
            Normalized amount as float
        """
        if amount is None:
            return 0.0
            
        if isinstance(amount, (int, float)):
            return float(amount)
            
        if isinstance(amount, str):
            # Remove currency symbols and commas
            amount_str = re.sub(r'[UGX,$\s]', '', amount)
            try:
                return float(amount_str)
            except ValueError:
                logger.warning(f"Could not parse amount: {amount}")
                return 0.0
                
        return 0.0
        
    def normalize_date(self, date_input) -> str:
        """
        Normalize date to ISO format string.
        
        Args:
            date_input: Raw date (string or datetime)
            
        Returns:
            ISO format date string
        """
        if isinstance(date_input, datetime):
            return date_input.isoformat()
            
        if isinstance(date_input, str):
            try:
                # Try to parse the date string
                parsed_date = date_parser.parse(date_input)
                return parsed_date.isoformat()
            except (ValueError, TypeError):
                logger.warning(f"Could not parse date: {date_input}")
                return datetime.now().isoformat()
                
        return datetime.now().isoformat()
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text fields.
        
        Args:
            text: Raw text string
            
        Returns:
            Cleaned text string
        """
        if not text or not isinstance(text, str):
            return ''
            
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        cleaned = re.sub(r'[^\w\s\-.,()]', '', cleaned)
        
        return cleaned
        
    def generate_transaction_id(self, transaction: Dict) -> str:
        """
        Generate a unique transaction ID based on transaction data.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Generated transaction ID
        """
        # Create hash based on key transaction attributes
        import hashlib
        
        key_data = [
            str(transaction.get('transaction_date', '')),
            str(transaction.get('amount', '')),
            str(transaction.get('sender_phone', '')),
            str(transaction.get('receiver_phone', '')),
            str(transaction.get('description', ''))
        ]
        
        data_string = '|'.join(key_data)
        hash_object = hashlib.md5(data_string.encode())
        return hash_object.hexdigest()[:12]  # First 12 characters
        
    def validate_transaction(self, transaction: Dict) -> bool:
        """
        Validate that a transaction has required fields and valid data.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['transaction_id', 'amount', 'transaction_date']
        
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                logger.warning(f"Missing required field: {field}")
                return False
                
        # Validate amount is positive
        if transaction['amount'] <= 0:
            logger.warning(f"Invalid amount: {transaction['amount']}")
            return False
            
        return True


def clean_and_normalize_data(transactions: List[Dict]) -> List[Dict]:
    """
    Main function to clean and normalize transaction data.
    
    Args:
        transactions: List of raw transaction dictionaries
        
    Returns:
        List of cleaned and normalized transactions
    """
    cleaner = DataCleaner()
    cleaned_transactions = cleaner.clean_transactions(transactions)
    
    # Filter out invalid transactions
    valid_transactions = [
        t for t in cleaned_transactions 
        if cleaner.validate_transaction(t)
    ]
    
    logger.info(f"Validated {len(valid_transactions)} out of {len(cleaned_transactions)} cleaned transactions")
    return valid_transactions


if __name__ == "__main__":
    # Example usage
    sample_transactions = [
        {
            'sender_phone': '0772123456',
            'amount': 'UGX 10,000',
            'transaction_date': '2023-10-15 14:30:00',
            'description': '  Payment for   goods  '
        }
    ]
    
    cleaned = clean_and_normalize_data(sample_transactions)
    print(f"Cleaned {len(cleaned)} transactions")
    for t in cleaned:
        print(t)
