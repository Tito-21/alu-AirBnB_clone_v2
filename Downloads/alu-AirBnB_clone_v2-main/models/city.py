#!/usr/bin/python3
"""
This module defines the City class.
"""
from sqlalchemy import Column, String, ForeignKey
from models.base_model import BaseModel, Base


class City(BaseModel, Base):
    """
    City class that inherits from BaseModel and Base.

    Attributes:
        name (str): The name of the city.
        state_id (str): The state id (foreign key to states.id).
    """
    __tablename__ = 'cities'

    name = Column(String(128), nullable=False)
    state_id = Column(String(60), ForeignKey('states.id'), nullable=False)
