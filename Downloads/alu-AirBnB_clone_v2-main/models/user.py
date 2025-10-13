#!/usr/bin/python3
"""
This module defines the User class.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class User(BaseModel, Base):
    """
    User class that inherits from BaseModel and Base.

    Attributes:
        email (str): The email of the user.
        password (str): The password of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        places (relationship): Relationship with Place objects.
        reviews (relationship): Relationship with Review objects.
    """
    __tablename__ = 'users'

    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)

    places = relationship(
        'Place',
        backref='user',
        cascade='all, delete, delete-orphan'
    )
    reviews = relationship(
        'Review',
        backref='user',
        cascade='all, delete, delete-orphan'
    )
