#!/usr/bin/python3
"""
This module defines the Amenity class.
"""
import os
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class Amenity(BaseModel, Base):
    """
    Amenity class that inherits from BaseModel and Base.

    Attributes:
        name (str): The name of the amenity.
        place_amenities (relationship): Relationship with Place objects.
    """
    __tablename__ = 'amenities'

    name = Column(String(128), nullable=False)

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        place_amenities = relationship(
            'Place',
            secondary='place_amenity',
            viewonly=False,
            back_populates='amenities'
        )
