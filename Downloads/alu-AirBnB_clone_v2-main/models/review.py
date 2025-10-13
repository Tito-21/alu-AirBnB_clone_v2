#!/usr/bin/python3
"""
This module defines the Review class.
"""
from sqlalchemy import Column, String, ForeignKey
from models.base_model import BaseModel, Base


class Review(BaseModel, Base):
    """
    Review class that inherits from BaseModel and Base.

    Attributes:
        text (str): The review text.
        place_id (str): The place id (foreign key to places.id).
        user_id (str): The user id (foreign key to users.id).
    """
    __tablename__ = 'reviews'

    text = Column(String(1024), nullable=False)
    place_id = Column(String(60), ForeignKey('places.id'), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
