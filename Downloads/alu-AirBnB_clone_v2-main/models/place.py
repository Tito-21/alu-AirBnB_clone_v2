#!/usr/bin/python3
"""
This module defines the Place class.
"""
import os
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from models.base_model import BaseModel, Base

# Define the Many-to-Many relationship table
place_amenity = Table(
    'place_amenity',
    Base.metadata,
    Column(
        'place_id',
        String(60),
        ForeignKey('places.id'),
        primary_key=True,
        nullable=False
    ),
    Column(
        'amenity_id',
        String(60),
        ForeignKey('amenities.id'),
        primary_key=True,
        nullable=False
    )
)


class Place(BaseModel, Base):
    """
    Place class that inherits from BaseModel and Base.

    Attributes:
        city_id (str): The city id (foreign key to cities.id).
        user_id (str): The user id (foreign key to users.id).
        name (str): The name of the place.
        description (str): The description of the place.
        number_rooms (int): The number of rooms.
        number_bathrooms (int): The number of bathrooms.
        max_guest (int): The maximum number of guests.
        price_by_night (int): The price per night.
        latitude (float): The latitude coordinate.
        longitude (float): The longitude coordinate.
        reviews (relationship): Relationship with Review objects.
        amenities (relationship): Relationship with Amenity objects.
        amenity_ids (list): List of Amenity ids (for FileStorage).
    """
    __tablename__ = 'places'

    city_id = Column(String(60), ForeignKey('cities.id'), nullable=False)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=True)
    number_rooms = Column(Integer, nullable=False, default=0)
    number_bathrooms = Column(Integer, nullable=False, default=0)
    max_guest = Column(Integer, nullable=False, default=0)
    price_by_night = Column(Integer, nullable=False, default=0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        reviews = relationship(
            'Review',
            backref='place',
            cascade='all, delete, delete-orphan'
        )
        amenities = relationship(
            'Amenity',
            secondary=place_amenity,
            viewonly=False,
            back_populates='place_amenities'
        )
    else:
        amenity_ids = []

        @property
        def amenities(self):
            """
            Getter for FileStorage returning Amenity instances.

            Returns:
                list: List of Amenity instances based on amenity_ids.
            """
            from models import storage
            from models.amenity import Amenity
            amenity_list = []
            all_amenities = storage.all(Amenity)
            for amenity in all_amenities.values():
                if amenity.id in self.amenity_ids:
                    amenity_list.append(amenity)
            return amenity_list

        @amenities.setter
        def amenities(self, obj):
            """
            Setter for FileStorage to add Amenity.id.

            Args:
                obj: The Amenity object to add.
            """
            from models.amenity import Amenity
            if isinstance(obj, Amenity):
                if obj.id not in self.amenity_ids:
                    self.amenity_ids.append(obj.id)

        @property
        def reviews(self):
            """
            Getter for FileStorage returning Review instances.

            Returns:
                list: Review instances with place_id equals to Place.id
            """
            from models import storage
            from models.review import Review
            review_list = []
            all_reviews = storage.all(Review)
            for review in all_reviews.values():
                if review.place_id == self.id:
                    review_list.append(review)
            return review_list
