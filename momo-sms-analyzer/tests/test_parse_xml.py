"""
Unit tests for the XML parsing module.
"""

import unittest
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from etl.parse_xml import XMLParser, parse_sms_transactions


class TestXMLParser(unittest.TestCase):
    """Test cases for XMLParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = XMLParser()
        
        # Sample XML content for testing
        self.sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<smses>
    <sms address="+256772123456" date="1634567890000" body="You have sent UGX 50,000 to John Doe. Your balance is UGX 100,000" />
    <sms address="+256701987654" date="1634654290000" body="You have received UGX 25,000 from Jane Smith. Your balance is UGX 125,000" />
    <sms address="+256779555111" date="1634740690000" body="You have bought UGX 5,000 airtime. Your balance is UGX 120,000" />
</smses>"""
        
        # Invalid XML for testing error handling
        self.invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<smses>
    <sms address="+256772123456" date="invalid_date" body="Test message" />
    <sms address="" date="" body="" />
</smses>"""
    
    def create_temp_xml_file(self, content):
        """Create a temporary XML file with given content."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_validate_xml_structure_valid(self):
        """Test XML validation with valid XML."""
        xml_file = self.create_temp_xml_file(self.sample_xml)
        try:
            result = self.parser.validate_xml_structure(xml_file)
            self.assertTrue(result)
        finally:
            Path(xml_file).unlink()
    
    def test_validate_xml_structure_no_sms(self):
        """Test XML validation with no SMS elements."""
        empty_xml = """<?xml version="1.0" encoding="UTF-8"?><root></root>"""
        xml_file = self.create_temp_xml_file(empty_xml)
        try:
            result = self.parser.validate_xml_structure(xml_file)
            self.assertFalse(result)
        finally:
            Path(xml_file).unlink()
    
    def test_validate_xml_structure_invalid(self):
        """Test XML validation with invalid XML."""
        invalid_xml = """<?xml version="1.0" encoding="UTF-8"?><unclosed>"""
        xml_file = self.create_temp_xml_file(invalid_xml)
        try:
            result = self.parser.validate_xml_structure(xml_file)
            self.assertFalse(result)
        finally:
            Path(xml_file).unlink()
    
    def test_parse_xml_file_valid(self):
        """Test parsing valid XML file."""
        xml_file = self.create_temp_xml_file(self.sample_xml)
        try:
            transactions = self.parser.parse_xml_file(xml_file)
            
            self.assertEqual(len(transactions), 3)
            
            # Check first transaction
            tx1 = transactions[0]
            self.assertEqual(tx1['raw_sender'], '+256772123456')
            self.assertIn('You have sent UGX 50,000', tx1['raw_body'])
            self.assertIn('transaction_date', tx1)
            self.assertIn('parsed_at', tx1)
            
        finally:
            Path(xml_file).unlink()
    
    def test_parse_xml_file_nonexistent(self):
        """Test parsing non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_xml_file('nonexistent_file.xml')
    
    def test_extract_transaction_data(self):
        """Test transaction data extraction from SMS element."""
        # Create SMS element
        sms_element = ET.Element('sms')
        sms_element.set('address', '+256772123456')
        sms_element.set('date', '1634567890000')
        sms_element.set('body', 'Test SMS message')
        
        transaction = self.parser._extract_transaction_data(sms_element)
        
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['raw_sender'], '+256772123456')
        self.assertEqual(transaction['raw_body'], 'Test SMS message')
        self.assertIn('transaction_date', transaction)
        self.assertIn('parsed_at', transaction)
    
    def test_extract_transaction_data_invalid_date(self):
        """Test transaction data extraction with invalid date."""
        sms_element = ET.Element('sms')
        sms_element.set('address', '+256772123456')
        sms_element.set('date', 'invalid_date')
        sms_element.set('body', 'Test SMS message')
        
        transaction = self.parser._extract_transaction_data(sms_element)
        
        # Should still return a transaction with current date
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['raw_sender'], '+256772123456')
        self.assertIn('transaction_date', transaction)
    
    def test_extract_transaction_data_empty_attributes(self):
        """Test transaction data extraction with empty attributes."""
        sms_element = ET.Element('sms')
        
        transaction = self.parser._extract_transaction_data(sms_element)
        
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['raw_sender'], '')
        self.assertEqual(transaction['raw_body'], '')
    
    def test_save_to_dead_letter(self):
        """Test saving failed records to dead letter queue."""
        # Create a problematic SMS element
        sms_element = ET.Element('sms')
        sms_element.set('address', 'invalid')
        
        error_msg = "Test error message"
        
        # This should not raise an exception
        try:
            self.parser._save_to_dead_letter(sms_element, error_msg)
        except Exception as e:
            self.fail(f"save_to_dead_letter raised an exception: {e}")


class TestModuleFunctions(unittest.TestCase):
    """Test cases for module-level functions."""
    
    def test_parse_sms_transactions(self):
        """Test the main parse_sms_transactions function."""
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<smses>
    <sms address="+256772123456" date="1634567890000" body="Test message" />
</smses>"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        temp_file.write(sample_xml)
        temp_file.close()
        
        try:
            transactions = parse_sms_transactions(temp_file.name)
            
            self.assertEqual(len(transactions), 1)
            self.assertEqual(transactions[0]['raw_sender'], '+256772123456')
            
        finally:
            Path(temp_file.name).unlink()
    
    def test_parse_sms_transactions_invalid_structure(self):
        """Test parsing with invalid XML structure."""
        invalid_xml = """<?xml version="1.0" encoding="UTF-8"?><root></root>"""
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False)
        temp_file.write(invalid_xml)
        temp_file.close()
        
        try:
            with self.assertRaises(ValueError):
                parse_sms_transactions(temp_file.name)
        finally:
            Path(temp_file.name).unlink()


if __name__ == '__main__':
    unittest.main()
