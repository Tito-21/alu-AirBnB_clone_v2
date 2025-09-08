"""
Unit tests for the data cleaning and normalization module.
"""

import unittest
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from etl.clean_normalize import DataCleaner, clean_and_normalize_data


class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = DataCleaner()
    
    def test_normalize_phone_number_full_format(self):
        """Test phone number normalization with full international format."""
        result = self.cleaner.normalize_phone_number('+256772123456')
        self.assertEqual(result, '+256772123456')
    
    def test_normalize_phone_number_country_code_only(self):
        """Test phone number normalization with country code without plus."""
        result = self.cleaner.normalize_phone_number('256772123456')
        self.assertEqual(result, '+256772123456')
    
    def test_normalize_phone_number_local_format(self):
        """Test phone number normalization with local format."""
        result = self.cleaner.normalize_phone_number('0772123456')
        self.assertEqual(result, '+256772123456')
    
    def test_normalize_phone_number_nine_digits(self):
        """Test phone number normalization with 9 digits."""
        result = self.cleaner.normalize_phone_number('772123456')
        self.assertEqual(result, '+256772123456')
    
    def test_normalize_phone_number_with_spaces_and_dashes(self):
        """Test phone number normalization with formatting characters."""
        result = self.cleaner.normalize_phone_number('+256-772-123-456')
        self.assertEqual(result, '+256772123456')
        
        result = self.cleaner.normalize_phone_number('0772 123 456')
        self.assertEqual(result, '+256772123456')
    
    def test_normalize_phone_number_empty(self):
        """Test phone number normalization with empty input."""
        result = self.cleaner.normalize_phone_number('')
        self.assertEqual(result, '')
        
        result = self.cleaner.normalize_phone_number(None)
        self.assertEqual(result, '')
    
    def test_identify_network_mtn(self):
        """Test network identification for MTN numbers."""
        result = self.cleaner.identify_network('+256772123456')
        self.assertEqual(result, 'MTN')
        
        result = self.cleaner.identify_network('+256782123456')
        self.assertEqual(result, 'MTN')
        
        result = self.cleaner.identify_network('+256762123456')
        self.assertEqual(result, 'MTN')
    
    def test_identify_network_airtel(self):
        """Test network identification for Airtel numbers."""
        result = self.cleaner.identify_network('+256752123456')
        self.assertEqual(result, 'AIRTEL')
        
        result = self.cleaner.identify_network('+256702123456')
        self.assertEqual(result, 'AIRTEL')
        
        result = self.cleaner.identify_network('+256742123456')
        self.assertEqual(result, 'AIRTEL')
    
    def test_identify_network_africell(self):
        """Test network identification for Africell numbers."""
        result = self.cleaner.identify_network('+256792123456')
        self.assertEqual(result, 'AFRICELL')
    
    def test_identify_network_unknown(self):
        """Test network identification for unknown numbers."""
        result = self.cleaner.identify_network('+256712123456')  # Non-existent prefix
        self.assertEqual(result, 'UNKNOWN')
        
        result = self.cleaner.identify_network('')
        self.assertEqual(result, 'UNKNOWN')
    
    def test_normalize_amount_integer(self):
        """Test amount normalization with integer input."""
        result = self.cleaner.normalize_amount(50000)
        self.assertEqual(result, 50000.0)
    
    def test_normalize_amount_float(self):
        """Test amount normalization with float input."""
        result = self.cleaner.normalize_amount(50000.50)
        self.assertEqual(result, 50000.50)
    
    def test_normalize_amount_string_with_currency(self):
        """Test amount normalization with currency string."""
        result = self.cleaner.normalize_amount('UGX 50,000')
        self.assertEqual(result, 50000.0)
        
        result = self.cleaner.normalize_amount('$ 1,250.50')
        self.assertEqual(result, 1250.50)
    
    def test_normalize_amount_string_plain(self):
        """Test amount normalization with plain string."""
        result = self.cleaner.normalize_amount('50000')
        self.assertEqual(result, 50000.0)
        
        result = self.cleaner.normalize_amount('50,000.50')
        self.assertEqual(result, 50000.50)
    
    def test_normalize_amount_invalid(self):
        """Test amount normalization with invalid input."""
        result = self.cleaner.normalize_amount('invalid')
        self.assertEqual(result, 0.0)
        
        result = self.cleaner.normalize_amount(None)
        self.assertEqual(result, 0.0)
        
        result = self.cleaner.normalize_amount('')
        self.assertEqual(result, 0.0)
    
    def test_normalize_date_datetime_object(self):
        """Test date normalization with datetime object."""
        test_date = datetime(2023, 10, 15, 14, 30, 0)
        result = self.cleaner.normalize_date(test_date)
        self.assertEqual(result, test_date.isoformat())
    
    def test_normalize_date_string(self):
        """Test date normalization with string input."""
        result = self.cleaner.normalize_date('2023-10-15 14:30:00')
        self.assertIn('2023-10-15', result)
        
        result = self.cleaner.normalize_date('Oct 15, 2023 2:30 PM')
        self.assertIn('2023-10-15', result)
    
    def test_normalize_date_invalid(self):
        """Test date normalization with invalid input."""
        result = self.cleaner.normalize_date('invalid_date')
        # Should return current date in ISO format
        self.assertIsInstance(result, str)
        self.assertIn('-', result)  # Should contain date separators
    
    def test_clean_text(self):
        """Test text cleaning and normalization."""
        result = self.cleaner.clean_text('  This   is   a   test  ')
        self.assertEqual(result, 'This is a test')
        
        result = self.cleaner.clean_text('Text with @special #characters!')
        self.assertEqual(result, 'Text with special characters')
        
        result = self.cleaner.clean_text('')
        self.assertEqual(result, '')
        
        result = self.cleaner.clean_text(None)
        self.assertEqual(result, '')
    
    def test_generate_transaction_id(self):
        """Test transaction ID generation."""
        transaction = {
            'transaction_date': '2023-10-15T14:30:00',
            'amount': 50000,
            'sender_phone': '+256772123456',
            'receiver_phone': '+256701987654',
            'description': 'Test transaction'
        }
        
        result = self.cleaner.generate_transaction_id(transaction)
        
        # Should return a 12-character hash
        self.assertEqual(len(result), 12)
        self.assertIsInstance(result, str)
        
        # Same input should generate same ID
        result2 = self.cleaner.generate_transaction_id(transaction)
        self.assertEqual(result, result2)
        
        # Different input should generate different ID
        transaction['amount'] = 60000
        result3 = self.cleaner.generate_transaction_id(transaction)
        self.assertNotEqual(result, result3)
    
    def test_validate_transaction_valid(self):
        """Test transaction validation with valid data."""
        transaction = {
            'transaction_id': 'tx_123',
            'amount': 50000,
            'transaction_date': '2023-10-15T14:30:00'
        }
        
        result = self.cleaner.validate_transaction(transaction)
        self.assertTrue(result)
    
    def test_validate_transaction_missing_fields(self):
        """Test transaction validation with missing required fields."""
        transaction = {
            'amount': 50000,
            'transaction_date': '2023-10-15T14:30:00'
            # Missing transaction_id
        }
        
        result = self.cleaner.validate_transaction(transaction)
        self.assertFalse(result)
    
    def test_validate_transaction_zero_amount(self):
        """Test transaction validation with zero amount."""
        transaction = {
            'transaction_id': 'tx_123',
            'amount': 0,
            'transaction_date': '2023-10-15T14:30:00'
        }
        
        result = self.cleaner.validate_transaction(transaction)
        self.assertFalse(result)
    
    def test_validate_transaction_negative_amount(self):
        """Test transaction validation with negative amount."""
        transaction = {
            'transaction_id': 'tx_123',
            'amount': -1000,
            'transaction_date': '2023-10-15T14:30:00'
        }
        
        result = self.cleaner.validate_transaction(transaction)
        self.assertFalse(result)
    
    def test_clean_transaction_complete(self):
        """Test complete transaction cleaning."""
        raw_transaction = {
            'raw_sender': '0772123456',
            'sender_phone': '0772123456',
            'receiver_phone': '256701987654',
            'amount': 'UGX 50,000',
            'balance_before': '100,000',
            'balance_after': '50,000.50',
            'fees': '500',
            'transaction_date': '2023-10-15 14:30:00',
            'description': '  Payment  for  goods  ',
        }
        
        result = self.cleaner.clean_transaction(raw_transaction)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['sender_phone'], '+256772123456')
        self.assertEqual(result['receiver_phone'], '+256701987654')
        self.assertEqual(result['amount'], 50000.0)
        self.assertEqual(result['balance_before'], 100000.0)
        self.assertEqual(result['balance_after'], 50000.50)
        self.assertEqual(result['fees'], 500.0)
        self.assertEqual(result['description'], 'Payment for goods')
        self.assertIn('transaction_id', result)
        self.assertEqual(result['sender_network'], 'MTN')
        self.assertEqual(result['receiver_network'], 'AIRTEL')


class TestModuleFunctions(unittest.TestCase):
    """Test cases for module-level functions."""
    
    def test_clean_and_normalize_data(self):
        """Test the main clean_and_normalize_data function."""
        raw_transactions = [
            {
                'sender_phone': '0772123456',
                'amount': 'UGX 50,000',
                'transaction_date': '2023-10-15 14:30:00',
                'description': 'Test transaction 1'
            },
            {
                'sender_phone': '0701987654',
                'amount': '25000',
                'transaction_date': '2023-10-15 15:30:00',
                'description': 'Test transaction 2'
            },
            {
                # Invalid transaction (no amount)
                'sender_phone': '0779555111',
                'transaction_date': '2023-10-15 16:30:00',
                'description': 'Invalid transaction'
            }
        ]
        
        result = clean_and_normalize_data(raw_transactions)
        
        # Should return only valid transactions
        self.assertEqual(len(result), 2)
        
        # Check that transactions are properly cleaned
        tx1 = result[0]
        self.assertEqual(tx1['sender_phone'], '+256772123456')
        self.assertEqual(tx1['amount'], 50000.0)
        self.assertEqual(tx1['sender_network'], 'MTN')
        self.assertIn('transaction_id', tx1)
        
        tx2 = result[1]
        self.assertEqual(tx2['sender_phone'], '+256701987654')
        self.assertEqual(tx2['amount'], 25000.0)
        self.assertEqual(tx2['sender_network'], 'AIRTEL')


if __name__ == '__main__':
    unittest.main()
