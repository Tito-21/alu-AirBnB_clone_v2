"""
FastAPI Application for MoMo SMS Analytics

Provides REST API endpoints for accessing transaction data and analytics.
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from datetime import datetime

from .db import DatabaseManager
from .schemas import Transaction, AnalyticsSummary, TransactionFilter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MoMo SMS Analytics API",
    description="REST API for accessing MoMo SMS transaction data and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database manager instance
db_manager = DatabaseManager()


@app.get("/")
async def root():
    """API root endpoint with basic information."""
    return {
        "message": "MoMo SMS Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        analytics = db_manager.get_analytics_data()
        return {
            "status": "healthy",
            "database": "connected",
            "total_transactions": analytics.get("total_transactions", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by transaction category"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type (DEBIT/CREDIT)"),
    network: Optional[str] = Query(None, description="Filter by network provider")
):
    """Get list of transactions with optional filtering."""
    try:
        # Build filters
        filters = {}
        if category:
            filters['category'] = category.upper()
        if transaction_type:
            filters['transaction_type'] = transaction_type.upper()
        if network:
            filters['sender_network'] = network.upper()
        
        # Get transactions from database
        transactions = db_manager.get_transactions(
            limit=limit + skip,  # Get extra records for skipping
            filters=filters if filters else None
        )
        
        # Apply skip and limit
        paginated_transactions = transactions[skip:skip + limit]
        
        logger.info(f"Retrieved {len(paginated_transactions)} transactions")
        return paginated_transactions
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str = Path(..., description="Transaction ID")
):
    """Get a specific transaction by ID."""
    try:
        filters = {'transaction_id': transaction_id}
        transactions = db_manager.get_transactions(limit=1, filters=filters)
        
        if not transactions:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        logger.info(f"Retrieved transaction: {transaction_id}")
        return transactions[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics():
    """Get comprehensive analytics summary."""
    try:
        analytics_data = db_manager.get_analytics_data()
        
        if not analytics_data:
            raise HTTPException(status_code=404, detail="No analytics data available")
        
        # Transform data for response
        summary = AnalyticsSummary(
            total_transactions=analytics_data.get('total_transactions', 0),
            total_amount=analytics_data.get('total_amount', 0),
            by_category=analytics_data.get('by_category', []),
            by_type=analytics_data.get('by_type', []),
            by_network=analytics_data.get('by_network', []),
            monthly_trends=analytics_data.get('monthly_trends', []),
            generated_at=datetime.now()
        )
        
        logger.info("Generated analytics summary")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/categories")
async def get_categories():
    """Get list of available transaction categories."""
    try:
        analytics_data = db_manager.get_analytics_data()
        categories = [item['category'] for item in analytics_data.get('by_category', [])]
        
        return {
            "categories": categories,
            "count": len(categories),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/networks")
async def get_networks():
    """Get list of available network providers."""
    try:
        analytics_data = db_manager.get_analytics_data()
        networks = [item['network'] for item in analytics_data.get('by_network', [])]
        
        return {
            "networks": networks,
            "count": len(networks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving networks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/stats")
async def get_stats():
    """Get basic statistics about the dataset."""
    try:
        analytics_data = db_manager.get_analytics_data()
        
        # Calculate additional stats
        avg_amount = 0
        if analytics_data.get('total_transactions', 0) > 0:
            avg_amount = analytics_data.get('total_amount', 0) / analytics_data['total_transactions']
        
        return {
            "total_transactions": analytics_data.get('total_transactions', 0),
            "total_amount": analytics_data.get('total_amount', 0),
            "average_amount": round(avg_amount, 2),
            "categories_count": len(analytics_data.get('by_category', [])),
            "networks_count": len(analytics_data.get('by_network', [])),
            "months_covered": len(analytics_data.get('monthly_trends', [])),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
