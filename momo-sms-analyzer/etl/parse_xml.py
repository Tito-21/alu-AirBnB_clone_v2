"""
XML Parsing Module

Handles parsing of MoMo SMS XML data using ElementTree/lxml.
Extracts transaction data from XML structure.
"""

import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

from .config import DEAD_LETTER_PATH, MAX_RETRIES

# Setup logging
logger = logging.getLogger('etl.parse_xml')


class XMLParser:
    """XML Parser for MoMo SMS transaction data."""
    
    def __init__(self, dead_letter_path: str = DEAD_LETTER_PATH):
        self.dead_letter_path = Path(dead_letter_path)
        self.dead_letter_path.mkdir(parents=True, exist_ok=True)
        self.failed_records = []
        
    def parse_xml_file(self, xml_file_path: str) -> List[Dict]:
        """
        Parse XML file and extract transaction records.
        
        Args:
            xml_file_path: Path to the XML file
            
        Returns:
            List of transaction dictionaries
        """
        logger.info(f"Starting XML parsing: {xml_file_path}")
        
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            transactions = []
            for sms_element in root.findall('.//sms'):  # Assuming SMS elements
                try:
                    transaction = self._extract_transaction_data(sms_element)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    logger.warning(f"Failed to parse SMS element: {e}")
                    self._save_to_dead_letter(sms_element, str(e))
                    
            logger.info(f"Successfully parsed {len(transactions)} transactions")
            return transactions
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise
        except FileNotFoundError:
            logger.error(f"XML file not found: {xml_file_path}")
            raise
            
    def _extract_transaction_data(self, sms_element: ET.Element) -> Optional[Dict]:
        """
        Extract transaction data from SMS XML element.
        
        Args:
            sms_element: XML element containing SMS data
            
        Returns:
            Transaction dictionary or None if extraction fails
        """
        try:
            # Extract basic SMS attributes
            sender = sms_element.get('address', '')
            timestamp = sms_element.get('date', '')
            body = sms_element.get('body', '')
            
            # Parse timestamp (assumes Unix timestamp in milliseconds)
            if timestamp:
                transaction_date = datetime.fromtimestamp(int(timestamp) / 1000)
            else:
                transaction_date = datetime.now()
            
            # Basic transaction structure
            transaction = {
                'raw_sender': sender,
                'transaction_date': transaction_date.isoformat(),
                'raw_body': body,
                'parsed_at': datetime.now().isoformat()
            }
            
            # Additional parsing logic will be implemented based on actual SMS format
            # For now, returning basic structure
            return transaction
            
        except Exception as e:
            logger.error(f"Error extracting transaction data: {e}")
            return None
            
    def _save_to_dead_letter(self, element: ET.Element, error_msg: str):
        """
        Save failed XML elements to dead letter queue.
        
        Args:
            element: Failed XML element
            error_msg: Error message
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"failed_sms_{timestamp}.xml"
            filepath = self.dead_letter_path / filename
            
            # Create a new XML tree with the failed element
            root = ET.Element("failed_record")
            root.set("error", error_msg)
            root.set("timestamp", datetime.now().isoformat())
            root.append(element)
            
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"Saved failed record to dead letter: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save to dead letter: {e}")
            
    def validate_xml_structure(self, xml_file_path: str) -> bool:
        """
        Validate XML file structure before processing.
        
        Args:
            xml_file_path: Path to XML file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            
            # Basic validation - check for SMS elements
            sms_elements = root.findall('.//sms')
            if not sms_elements:
                logger.warning("No SMS elements found in XML")
                return False
                
            logger.info(f"XML validation passed: {len(sms_elements)} SMS elements found")
            return True
            
        except ET.ParseError as e:
            logger.error(f"XML validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            return False


def parse_sms_transactions(xml_file_path: str) -> List[Dict]:
    """
    Main function to parse SMS transactions from XML file.
    
    Args:
        xml_file_path: Path to the XML file
        
    Returns:
        List of transaction dictionaries
    """
    parser = XMLParser()
    
    if not parser.validate_xml_structure(xml_file_path):
        raise ValueError("Invalid XML structure")
        
    return parser.parse_xml_file(xml_file_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python parse_xml.py <xml_file_path>")
        sys.exit(1)
        
    xml_file = sys.argv[1]
    transactions = parse_sms_transactions(xml_file)
    print(f"Parsed {len(transactions)} transactions")
