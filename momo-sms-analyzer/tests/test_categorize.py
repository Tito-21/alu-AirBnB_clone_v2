"""
Unit tests for the transaction categorization module.
"""

import unittest
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from etl.categorize import TransactionCategorizer, categorize_transactions, get_transaction_insights


class TestTransactionCategorizer(unittest.TestCase):
    """Test cases for TransactionCategorizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.categorizer = TransactionCategorizer()
    
    def test_categorize_by_description_transfer(self):
        """Test categorization by description for transfers."""
        result = self.categorizer._categorize_by_description('Money transfer to John')
        self.assertEqual(result, 'TRANSFER')
        
        result = self.categorizer._categorize_by_description('Send money to friend')
        self.assertEqual(result, 'TRANSFER')
    
    def test_categorize_by_description_deposit(self):
        """Test categorization by description for deposits."""
        result = self.categorizer._categorize_by_description('Deposit from salary')
        self.assertEqual(result, 'DEPOSIT')
        
        result = self.categorizer._categorize_by_description('Received money from client')
        self.assertEqual(result, 'DEPOSIT')
    
    def test_categorize_by_description_payment(self):
        """Test categorization by description for payments."""
        result = self.categorizer._categorize_by_description('Payment for goods')
        self.assertEqual(result, 'PAYMENT')
        
        result = self.categorizer._categorize_by_description('Purchase at shop')
        self.assertEqual(result, 'PAYMENT')
    
    def test_categorize_by_description_airtime(self):
        """Test categorization by description for airtime."""
        result = self.categorizer._categorize_by_description('Airtime purchase')
        self.assertEqual(result, 'AIRTIME')
        
        result = self.categorizer._categorize_by_description('Credit top up')
        self.assertEqual(result, 'AIRTIME')
    
    def test_categorize_by_description_no_match(self):
        """Test categorization by description with no match."""
        result = self.categorizer._categorize_by_description('Random text')
        self.assertEqual(result, '')
        
        result = self.categorizer._categorize_by_description('')
        self.assertEqual(result, '')
    
    def test_categorize_by_body_transfer(self):
        """Test categorization by SMS body for transfers."""
        result = self.categorizer._categorize_by_body('You have sent UGX 50,000 to John Doe')
        self.assertEqual(result, 'TRANSFER')
        
        result = self.categorizer._categorize_by_body('Money sent to +256772123456')
        self.assertEqual(result, 'TRANSFER')
    
    def test_categorize_by_body_deposit(self):
        """Test categorization by SMS body for deposits."""
        result = self.categorizer._categorize_by_body('You have received UGX 25,000 from Jane')
        self.assertEqual(result, 'DEPOSIT')
        
        result = self.categorizer._categorize_by_body('Money received from +256701987654')
        self.assertEqual(result, 'DEPOSIT')
    
    def test_categorize_by_body_withdrawal(self):
        """Test categorization by SMS body for withdrawals."""
        result = self.categorizer._categorize_by_body('Cash out of UGX 100,000')
        self.assertEqual(result, 'WITHDRAWAL')
        
        result = self.categorizer._categorize_by_body('Withdrawal successful')
        self.assertEqual(result, 'WITHDRAWAL')
    
    def test_categorize_by_body_airtime(self):
        """Test categorization by SMS body for airtime."""
        result = self.categorizer._categorize_by_body('You have bought UGX 5,000 airtime')
        self.assertEqual(result, 'AIRTIME')
        
        result = self.categorizer._categorize_by_body('Airtime top up successful')
        self.assertEqual(result, 'AIRTIME')
    
    def test_infer_transaction_type_debit_categories(self):
        """Test transaction type inference for debit categories."""
        transaction = {'category': 'TRANSFER'}
        result = self.categorizer._infer_transaction_type(transaction, 'TRANSFER')
        self.assertEqual(result, 'DEBIT')
        
        transaction = {'category': 'PAYMENT'}
        result = self.categorizer._infer_transaction_type(transaction, 'PAYMENT')
        self.assertEqual(result, 'DEBIT')
        
        transaction = {'category': 'WITHDRAWAL'}
        result = self.categorizer._infer_transaction_type(transaction, 'WITHDRAWAL')
        self.assertEqual(result, 'DEBIT')
    
    def test_infer_transaction_type_credit_categories(self):
        """Test transaction type inference for credit categories."""
        transaction = {'category': 'DEPOSIT'}
        result = self.categorizer._infer_transaction_type(transaction, 'DEPOSIT')
        self.assertEqual(result, 'CREDIT')
    
    def test_infer_transaction_type_balance_based(self):
        """Test transaction type inference based on balance changes."""
        # Credit - balance increased
        transaction = {
            'balance_before': 50000,
            'balance_after': 75000
        }
        result = self.categorizer._infer_transaction_type(transaction, 'OTHER')
        self.assertEqual(result, 'CREDIT')
        
        # Debit - balance decreased
        transaction = {
            'balance_before': 100000,
            'balance_after': 50000
        }
        result = self.categorizer._infer_transaction_type(transaction, 'OTHER')
        self.assertEqual(result, 'DEBIT')
    
    def test_infer_transaction_type_sms_based(self):
        """Test transaction type inference based on SMS body."""
        transaction = {'raw_body': 'You have sent money to John'}
        result = self.categorizer._infer_transaction_type(transaction, 'OTHER')
        self.assertEqual(result, 'DEBIT')
        
        transaction = {'raw_body': 'You have received money from Jane'}
        result = self.categorizer._infer_transaction_type(transaction, 'OTHER')
        self.assertEqual(result, 'CREDIT')
    
    def test_categorize_by_amount(self):
        """Test amount categorization."""
        result = self.categorizer._categorize_by_amount(500)
        self.assertEqual(result, 'SMALL')
        
        result = self.categorizer._categorize_by_amount(25000)
        self.assertEqual(result, 'MEDIUM')
        
        result = self.categorizer._categorize_by_amount(250000)
        self.assertEqual(result, 'LARGE')
        
        result = self.categorizer._categorize_by_amount(1000000)
        self.assertEqual(result, 'VERY_LARGE')
    
    def test_categorize_by_time(self):
        """Test time-based categorization."""
        # Morning (8 AM)
        result = self.categorizer._categorize_by_time('2023-10-15T08:30:00')
        self.assertEqual(result, 'MORNING')
        
        # Afternoon (2 PM)
        result = self.categorizer._categorize_by_time('2023-10-15T14:30:00')
        self.assertEqual(result, 'AFTERNOON')
        
        # Evening (7 PM)
        result = self.categorizer._categorize_by_time('2023-10-15T19:30:00')
        self.assertEqual(result, 'EVENING')
        
        # Night (11 PM)
        result = self.categorizer._categorize_by_time('2023-10-15T23:30:00')
        self.assertEqual(result, 'NIGHT')
        
        # Invalid date
        result = self.categorizer._categorize_by_time('invalid_date')
        self.assertEqual(result, 'UNKNOWN')
    
    def test_categorize_transaction_complete(self):
        """Test complete transaction categorization."""
        transaction = {
            'description': 'Transfer to John',
            'raw_body': 'You have sent UGX 50,000 to John Doe',
            'amount': 50000,
            'transaction_date': '2023-10-15T14:30:00'
        }
        
        result = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(result['category'], 'TRANSFER')
        self.assertEqual(result['transaction_type'], 'DEBIT')
        self.assertEqual(result['amount_category'], 'MEDIUM')
        self.assertEqual(result['time_category'], 'AFTERNOON')
        
        # Original fields should be preserved
        self.assertEqual(result['description'], 'Transfer to John')
        self.assertEqual(result['amount'], 50000)
    
    def test_categorize_transactions_list(self):
        """Test categorizing a list of transactions."""
        transactions = [
            {
                'description': 'Transfer money',
                'amount': 25000,
                'transaction_date': '2023-10-15T10:00:00'
            },
            {
                'raw_body': 'You have received UGX 15,000',
                'amount': 15000,
                'transaction_date': '2023-10-15T16:00:00'
            }
        ]
        
        result = self.categorizer.categorize_transactions(transactions)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['category'], 'TRANSFER')
        self.assertEqual(result[0]['transaction_type'], 'DEBIT')
        self.assertEqual(result[1]['category'], 'DEPOSIT')
        self.assertEqual(result[1]['transaction_type'], 'CREDIT')
    
    def test_get_category_statistics(self):
        """Test category statistics generation."""
        transactions = [
            {
                'category': 'TRANSFER',
                'transaction_type': 'DEBIT',
                'amount_category': 'MEDIUM',
                'time_category': 'MORNING'
            },
            {
                'category': 'TRANSFER',
                'transaction_type': 'DEBIT',
                'amount_category': 'SMALL',
                'time_category': 'AFTERNOON'
            },
            {
                'category': 'DEPOSIT',
                'transaction_type': 'CREDIT',
                'amount_category': 'LARGE',
                'time_category': 'MORNING'
            }
        ]
        
        result = self.categorizer.get_category_statistics(transactions)
        
        self.assertEqual(result['total_transactions'], 3)
        self.assertEqual(result['categories']['TRANSFER'], 2)
        self.assertEqual(result['categories']['DEPOSIT'], 1)
        self.assertEqual(result['transaction_types']['DEBIT'], 2)
        self.assertEqual(result['transaction_types']['CREDIT'], 1)
        self.assertEqual(result['time_categories']['MORNING'], 2)
        self.assertEqual(result['time_categories']['AFTERNOON'], 1)


class TestModuleFunctions(unittest.TestCase):
    """Test cases for module-level functions."""
    
    def test_categorize_transactions(self):
        """Test the main categorize_transactions function."""
        transactions = [
            {
                'description': 'Send money to friend',
                'amount': 30000,
                'transaction_date': '2023-10-15T12:00:00'
            },
            {
                'raw_body': 'Airtime purchase of UGX 5,000',
                'amount': 5000,
                'transaction_date': '2023-10-15T18:00:00'
            }
        ]
        
        result = categorize_transactions(transactions)
        
        self.assertEqual(len(result), 2)
        
        # Check first transaction
        tx1 = result[0]
        self.assertEqual(tx1['category'], 'TRANSFER')
        self.assertEqual(tx1['transaction_type'], 'DEBIT')
        self.assertEqual(tx1['amount_category'], 'MEDIUM')
        self.assertEqual(tx1['time_category'], 'AFTERNOON')
        
        # Check second transaction
        tx2 = result[1]
        self.assertEqual(tx2['category'], 'AIRTIME')
        self.assertEqual(tx2['transaction_type'], 'DEBIT')
        self.assertEqual(tx2['amount_category'], 'SMALL')
        self.assertEqual(tx2['time_category'], 'EVENING')
    
    def test_get_transaction_insights(self):
        """Test transaction insights generation."""
        transactions = [
            {
                'category': 'TRANSFER',
                'transaction_type': 'DEBIT',
                'amount_category': 'MEDIUM',
                'time_category': 'MORNING'
            },
            {
                'category': 'TRANSFER',
                'transaction_type': 'DEBIT',
                'amount_category': 'SMALL',
                'time_category': 'AFTERNOON'
            },
            {
                'category': 'DEPOSIT',
                'transaction_type': 'CREDIT',
                'amount_category': 'LARGE',
                'time_category': 'MORNING'
            }
        ]
        
        result = get_transaction_insights(transactions)
        
        self.assertIn('statistics', result)
        self.assertIn('insights', result)
        
        stats = result['statistics']
        insights = result['insights']
        
        self.assertEqual(stats['total_transactions'], 3)
        self.assertEqual(insights['most_common_category'], 'TRANSFER')
        self.assertEqual(insights['most_common_time'], 'MORNING')
        self.assertIsInstance(insights['debit_credit_ratio'], float)


if __name__ == '__main__':
    unittest.main()
