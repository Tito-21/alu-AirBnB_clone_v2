"""
Pydantic Schemas for API Response Models

Defines the data structures for API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Transaction(BaseModel):
    """Transaction response model."""
    
    id: Optional[int] = Field(None, description="Database record ID")
    transaction_id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="UGX", description="Currency code")
    transaction_date: str = Field(..., description="Transaction datetime in ISO format")
    transaction_type: str = Field(..., description="Transaction type (DEBIT/CREDIT)")
    category: str = Field(..., description="Transaction category")
    sender_phone: Optional[str] = Field(None, description="Sender phone number")
    receiver_phone: Optional[str] = Field(None, description="Receiver phone number")
    sender_network: Optional[str] = Field(None, description="Sender network provider")
    receiver_network: Optional[str] = Field(None, description="Receiver network provider")
    description: Optional[str] = Field(None, description="Transaction description")
    balance_before: Optional[float] = Field(None, description="Balance before transaction")
    balance_after: Optional[float] = Field(None, description="Balance after transaction")
    fees: Optional[float] = Field(default=0, description="Transaction fees")
    status: str = Field(default="SUCCESS", description="Transaction status")
    created_at: Optional[str] = Field(None, description="Record creation timestamp")
    updated_at: Optional[str] = Field(None, description="Record update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "transaction_id": "tx_abc123",
                "amount": 50000.0,
                "currency": "UGX",
                "transaction_date": "2023-10-15T14:30:00",
                "transaction_type": "DEBIT",
                "category": "TRANSFER",
                "sender_phone": "+256772123456",
                "receiver_phone": "+256701987654",
                "sender_network": "MTN",
                "receiver_network": "AIRTEL",
                "description": "Money transfer to friend",
                "balance_before": 100000.0,
                "balance_after": 50000.0,
                "fees": 500.0,
                "status": "SUCCESS"
            }
        }


class CategorySummary(BaseModel):
    """Category summary model."""
    
    category: str = Field(..., description="Category name")
    count: int = Field(..., description="Number of transactions")
    amount: float = Field(..., description="Total amount for category")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "TRANSFER",
                "count": 150,
                "amount": 5500000.0
            }
        }


class TypeSummary(BaseModel):
    """Transaction type summary model."""
    
    type: str = Field(..., description="Transaction type")
    count: int = Field(..., description="Number of transactions")
    amount: float = Field(..., description="Total amount for type")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "DEBIT",
                "count": 120,
                "amount": 4500000.0
            }
        }


class NetworkSummary(BaseModel):
    """Network summary model."""
    
    network: str = Field(..., description="Network provider name")
    count: int = Field(..., description="Number of transactions")
    amount: float = Field(..., description="Total amount for network")

    class Config:
        json_schema_extra = {
            "example": {
                "network": "MTN",
                "count": 75,
                "amount": 3200000.0
            }
        }


class MonthlyTrend(BaseModel):
    """Monthly trend model."""
    
    month: str = Field(..., description="Month in YYYY-MM format")
    count: int = Field(..., description="Number of transactions in month")
    amount: float = Field(..., description="Total amount for month")

    class Config:
        json_schema_extra = {
            "example": {
                "month": "2023-10",
                "count": 85,
                "amount": 2750000.0
            }
        }


class AnalyticsSummary(BaseModel):
    """Comprehensive analytics summary model."""
    
    total_transactions: int = Field(..., description="Total number of transactions")
    total_amount: float = Field(..., description="Total transaction amount")
    by_category: List[CategorySummary] = Field(default=[], description="Breakdown by category")
    by_type: List[TypeSummary] = Field(default=[], description="Breakdown by transaction type")
    by_network: List[NetworkSummary] = Field(default=[], description="Breakdown by network")
    monthly_trends: List[MonthlyTrend] = Field(default=[], description="Monthly trend data")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "total_transactions": 500,
                "total_amount": 15750000.0,
                "by_category": [
                    {"category": "TRANSFER", "count": 200, "amount": 8000000.0},
                    {"category": "AIRTIME", "count": 150, "amount": 3500000.0}
                ],
                "by_type": [
                    {"type": "DEBIT", "count": 350, "amount": 12000000.0},
                    {"type": "CREDIT", "count": 150, "amount": 3750000.0}
                ],
                "by_network": [
                    {"network": "MTN", "count": 300, "amount": 9500000.0},
                    {"network": "AIRTEL", "count": 200, "amount": 6250000.0}
                ],
                "monthly_trends": [
                    {"month": "2023-09", "count": 220, "count": 7000000.0},
                    {"month": "2023-10", "count": 280, "amount": 8750000.0}
                ],
                "generated_at": "2023-10-15T14:30:00"
            }
        }


class TransactionFilter(BaseModel):
    """Transaction filtering parameters."""
    
    category: Optional[str] = Field(None, description="Filter by category")
    transaction_type: Optional[str] = Field(None, description="Filter by type (DEBIT/CREDIT)")
    network: Optional[str] = Field(None, description="Filter by network provider")
    min_amount: Optional[float] = Field(None, description="Minimum amount filter")
    max_amount: Optional[float] = Field(None, description="Maximum amount filter")
    date_from: Optional[str] = Field(None, description="Start date filter (ISO format)")
    date_to: Optional[str] = Field(None, description="End date filter (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "TRANSFER",
                "transaction_type": "DEBIT",
                "network": "MTN",
                "min_amount": 1000.0,
                "max_amount": 100000.0,
                "date_from": "2023-10-01T00:00:00",
                "date_to": "2023-10-31T23:59:59"
            }
        }


class APIResponse(BaseModel):
    """Generic API response wrapper."""
    
    success: bool = Field(default=True, description="Request success status")
    message: str = Field(default="Success", description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": {},
                "timestamp": "2023-10-15T14:30:00"
            }
        }
