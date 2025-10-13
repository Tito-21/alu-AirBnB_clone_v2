#!/usr/bin/python3
"""
This module defines the BaseModel class.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel:
    """
    BaseModel class that defines all common attributes/methods.
    """
    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """
        Initialize a BaseModel instance.

        Args:
            *args: Variable length argument list (not used).
            **kwargs: Arbitrary keyword arguments.
        """
        if kwargs:
            for key, value in kwargs.items():
                if key == '__class__':
                    continue
                if key in ['created_at', 'updated_at']:
                    if isinstance(value, str):
                        value = datetime.strptime(
                            value, '%Y-%m-%dT%H:%M:%S.%f')
                setattr(self, key, value)

            if 'id' not in kwargs:
                self.id = str(uuid.uuid4())
            if 'created_at' not in kwargs:
                self.created_at = datetime.utcnow()
            if 'updated_at' not in kwargs:
                self.updated_at = datetime.utcnow()
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    def __str__(self):
        """
        Return string representation of the BaseModel instance.

        Returns:
            str: String representation [<class>] (<id>) <__dict__>
        """
        return "[{}] ({}) {}".format(
            self.__class__.__name__,
            self.id,
            self.to_dict()
        )

    def save(self):
        """
        Update updated_at with current datetime and save to storage.
        """
        from models import storage
        self.updated_at = datetime.utcnow()
        storage.new(self)
        storage.save()

    def to_dict(self):
        """
        Return dictionary with all keys/values of __dict__.

        Returns:
            dict: Dictionary representation of the instance.
        """
        obj_dict = self.__dict__.copy()
        obj_dict['__class__'] = self.__class__.__name__

        if 'created_at' in obj_dict and isinstance(
                obj_dict['created_at'], datetime):
            obj_dict['created_at'] = obj_dict['created_at'].isoformat()
        if 'updated_at' in obj_dict and isinstance(
                obj_dict['updated_at'], datetime):
            obj_dict['updated_at'] = obj_dict['updated_at'].isoformat()

        # Remove _sa_instance_state if it exists
        if '_sa_instance_state' in obj_dict:
            del obj_dict['_sa_instance_state']

        return obj_dict

    def delete(self):
        """
        Delete the current instance from storage.
        """
        from models import storage
        storage.delete(self)
