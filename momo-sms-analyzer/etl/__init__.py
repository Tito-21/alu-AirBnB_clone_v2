"""
MoMo SMS Data ETL Package

This package handles the Extract, Transform, Load process for MoMo SMS transaction data.
Modules:
- parse_xml: XML parsing using ElementTree/lxml
- clean_normalize: Data cleaning and normalization
- categorize: Transaction categorization rules
- load_db: Database operations and table management
- run: CLI interface for ETL pipeline
"""

__version__ = "1.0.0"
__author__ = "MoMo Analytics Team"
