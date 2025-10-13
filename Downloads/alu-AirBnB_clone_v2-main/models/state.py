#!/usr/bin/python3
"""
This module defines the State class.
"""
import os
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base


class State(BaseModel, Base):
    """
    State class that inherits from BaseModel and Base.

    Attributes:
        name (str): The name of the state.
        cities (relationship): Relationship with City objects.
    """
    __tablename__ = 'states'

    name = Column(String(128), nullable=False)

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        cities = relationship(
            'City',
            backref='state',
            cascade='all, delete, delete-orphan'
        )
    else:
        @property
        def cities(self):
            """
            Getter for FileStorage returning list of City instances.

            Returns:
                list: City instances with state_id equals to State.id
            """
            from models import storage
            from models.city import City
            city_list = []
            all_cities = storage.all(City)
            for city in all_cities.values():
                if city.state_id == self.id:
                    city_list.append(city)
            return city_list
