"""
ETL Runner Module

CLI interface for the complete ETL pipeline: parse -> clean -> categorize -> load -> export JSON.
"""

import click
import logging.config
from pathlib import Path
from typing import Optional

from .config import LOGGING_CONFIG, XML_INPUT_PATH, DASHBOARD_JSON_PATH
from .parse_xml import parse_sms_transactions
from .clean_normalize import clean_and_normalize_data
from .categorize import categorize_transactions
from .load_db import load_transactions_to_db, export_dashboard_data

# Setup logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('etl.run')


@click.group()
@click.version_option()
def cli():
    """MoMo SMS Data ETL Pipeline
    
    Extract, Transform, and Load MoMo SMS transaction data.
    """
    pass


@cli.command()
@click.option('--xml-file', '-x', 
              default=XML_INPUT_PATH,
              help='Path to XML input file',
              type=click.Path(exists=True))
@click.option('--output-json', '-o',
              default=DASHBOARD_JSON_PATH,
              help='Path to output JSON file for dashboard',
              type=click.Path())
@click.option('--skip-validation', 
              is_flag=True,
              help='Skip XML validation step')
@click.option('--batch-size', '-b',
              default=1000,
              help='Batch size for processing transactions',
              type=int)
def run_full_pipeline(xml_file: str, output_json: str, skip_validation: bool, batch_size: int):
    """Run the complete ETL pipeline: parse -> clean -> categorize -> load -> export."""
    
    logger.info("Starting full ETL pipeline")
    logger.info(f"Input XML: {xml_file}")
    logger.info(f"Output JSON: {output_json}")
    
    try:
        # Step 1: Parse XML
        logger.info("Step 1: Parsing XML data")
        raw_transactions = parse_sms_transactions(xml_file)
        logger.info(f"Parsed {len(raw_transactions)} raw transactions")
        
        if not raw_transactions:
            logger.warning("No transactions found in XML file")
            return
            
        # Step 2: Clean and normalize
        logger.info("Step 2: Cleaning and normalizing data")
        clean_transactions = clean_and_normalize_data(raw_transactions)
        logger.info(f"Cleaned {len(clean_transactions)} transactions")
        
        # Step 3: Categorize
        logger.info("Step 3: Categorizing transactions")
        categorized_transactions = categorize_transactions(clean_transactions)
        logger.info(f"Categorized {len(categorized_transactions)} transactions")
        
        # Step 4: Load to database
        logger.info("Step 4: Loading to database")
        loaded_count = load_transactions_to_db(categorized_transactions)
        logger.info(f"Loaded {loaded_count} transactions to database")
        
        # Step 5: Export JSON for dashboard
        logger.info("Step 5: Exporting dashboard data")
        export_success = export_dashboard_data(output_json)
        
        if export_success:
            logger.info(f"Pipeline completed successfully! Dashboard data exported to {output_json}")
        else:
            logger.error("Pipeline completed with errors during export")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise click.ClickException(f"ETL pipeline failed: {e}")


@cli.command()
@click.option('--xml-file', '-x',
              required=True,
              help='Path to XML input file',
              type=click.Path(exists=True))
def parse_only(xml_file: str):
    """Parse XML file only and display basic statistics."""
    
    logger.info(f"Parsing XML file: {xml_file}")
    
    try:
        transactions = parse_sms_transactions(xml_file)
        
        click.echo(f"Successfully parsed {len(transactions)} transactions")
        
        # Display sample transaction
        if transactions:
            click.echo("\nSample transaction:")
            sample = transactions[0]
            for key, value in sample.items():
                click.echo(f"  {key}: {value}")
                
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        raise click.ClickException(f"XML parsing failed: {e}")


@cli.command()
@click.option('--output-json', '-o',
              default=DASHBOARD_JSON_PATH,
              help='Path to output JSON file',
              type=click.Path())
def export_only(output_json: str):
    """Export dashboard data from existing database."""
    
    logger.info(f"Exporting dashboard data to: {output_json}")
    
    try:
        success = export_dashboard_data(output_json)
        
        if success:
            click.echo(f"Dashboard data exported successfully to {output_json}")
        else:
            raise click.ClickException("Export failed")
            
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise click.ClickException(f"Export failed: {e}")


@cli.command()
@click.option('--category', '-c',
              help='Filter by category',
              type=str)
@click.option('--transaction-type', '-t',
              help='Filter by transaction type (DEBIT/CREDIT)',
              type=click.Choice(['DEBIT', 'CREDIT', 'UNKNOWN']))
@click.option('--limit', '-l',
              default=10,
              help='Number of transactions to display',
              type=int)
def view_transactions(category: Optional[str], transaction_type: Optional[str], limit: int):
    """View transactions from the database."""
    
    logger.info("Retrieving transactions from database")
    
    try:
        from .load_db import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if transaction_type:
            filters['transaction_type'] = transaction_type
            
        transactions = db_manager.get_transactions(limit=limit, filters=filters)
        
        if not transactions:
            click.echo("No transactions found")
            return
            
        click.echo(f"\nFound {len(transactions)} transactions:")
        click.echo("-" * 80)
        
        for tx in transactions:
            click.echo(f"ID: {tx['transaction_id']}")
            click.echo(f"Amount: {tx['currency']} {tx['amount']:,.2f}")
            click.echo(f"Type: {tx['transaction_type']} | Category: {tx['category']}")
            click.echo(f"Date: {tx['transaction_date']}")
            if tx['description']:
                click.echo(f"Description: {tx['description']}")
            click.echo("-" * 80)
            
    except Exception as e:
        logger.error(f"Failed to retrieve transactions: {e}")
        raise click.ClickException(f"Database query failed: {e}")


@cli.command()
def analytics():
    """Display analytics and statistics from the database."""
    
    logger.info("Generating analytics")
    
    try:
        from .load_db import DatabaseManager
        
        db_manager = DatabaseManager()
        analytics_data = db_manager.get_analytics_data()
        
        if not analytics_data:
            click.echo("No data available for analytics")
            return
            
        click.echo("\n=== MoMo Transaction Analytics ===\n")
        
        # Summary
        click.echo(f"Total Transactions: {analytics_data['total_transactions']:,}")
        click.echo(f"Total Amount: UGX {analytics_data['total_amount']:,.2f}")
        
        # By Category
        click.echo("\n--- By Category ---")
        for item in analytics_data.get('by_category', []):
            click.echo(f"{item['category']}: {item['count']:,} transactions (UGX {item['amount']:,.2f})")
            
        # By Type
        click.echo("\n--- By Transaction Type ---")
        for item in analytics_data.get('by_type', []):
            click.echo(f"{item['type']}: {item['count']:,} transactions (UGX {item['amount']:,.2f})")
            
        # By Network
        if analytics_data.get('by_network'):
            click.echo("\n--- By Network ---")
            for item in analytics_data['by_network']:
                click.echo(f"{item['network']}: {item['count']:,} transactions (UGX {item['amount']:,.2f})")
                
        # Monthly Trends
        if analytics_data.get('monthly_trends'):
            click.echo("\n--- Monthly Trends (Last 12 months) ---")
            for item in analytics_data['monthly_trends']:
                click.echo(f"{item['month']}: {item['count']:,} transactions (UGX {item['amount']:,.2f})")
                
    except Exception as e:
        logger.error(f"Analytics generation failed: {e}")
        raise click.ClickException(f"Analytics failed: {e}")


@cli.command()
def status():
    """Check the status of the ETL system."""
    
    click.echo("=== MoMo ETL System Status ===\n")
    
    # Check database
    try:
        from .load_db import DatabaseManager
        db_manager = DatabaseManager()
        analytics = db_manager.get_analytics_data()
        
        click.echo("✅ Database: Connected")
        click.echo(f"   Transactions: {analytics.get('total_transactions', 0):,}")
        
    except Exception as e:
        click.echo(f"❌ Database: Error - {e}")
        
    # Check input file
    input_path = Path(XML_INPUT_PATH)
    if input_path.exists():
        click.echo(f"✅ Input XML: Found ({input_path})")
    else:
        click.echo(f"⚠️  Input XML: Not found ({input_path})")
        
    # Check output directory
    output_path = Path(DASHBOARD_JSON_PATH)
    if output_path.parent.exists():
        click.echo(f"✅ Output Directory: Exists ({output_path.parent})")
    else:
        click.echo(f"❌ Output Directory: Missing ({output_path.parent})")
        
    # Check logs
    from .config import ETL_LOG_PATH
    log_path = Path(ETL_LOG_PATH)
    if log_path.exists():
        click.echo(f"✅ Log File: Exists ({log_path})")
    else:
        click.echo(f"⚠️  Log File: Not found ({log_path})")


if __name__ == '__main__':
    cli()
