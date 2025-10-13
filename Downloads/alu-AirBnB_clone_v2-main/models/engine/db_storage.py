#!/usr/bin/python3
"""
This module defines the DBStorage class for database storage.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity


class DBStorage:
    """
    DBStorage class for managing database storage using SQLAlchemy.

    Attributes:
        __engine: SQLAlchemy engine.
        __session: SQLAlchemy session.
    """
    __engine = None
    __session = None

    def __init__(self):
        """
        Initialize DBStorage instance.
        """
        user = os.getenv('HBNB_MYSQL_USER')
        password = os.getenv('HBNB_MYSQL_PWD')
        host = os.getenv('HBNB_MYSQL_HOST', 'localhost')
        database = os.getenv('HBNB_MYSQL_DB')

        # Create engine
        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                user, password, host, database
            ),
            pool_pre_ping=True
        )

        # Drop all tables if environment is test
        if os.getenv('HBNB_ENV') == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """
        Query all objects depending on the class name.

        Args:
            cls: Class to query (optional).

        Returns:
            dict: Dictionary of objects in <class-name>.<object-id> format
        """
        obj_dict = {}

        if cls:
            # Query specific class
            if isinstance(cls, str):
                cls = eval(cls)
            query = self.__session.query(cls)
            for obj in query.all():
                key = "{}.{}".format(obj.__class__.__name__, obj.id)
                obj_dict[key] = obj
        else:
            # Query all classes
            classes = [State, City, User, Place, Review, Amenity]
            for class_type in classes:
                query = self.__session.query(class_type)
                for obj in query.all():
                    key = "{}.{}".format(obj.__class__.__name__, obj.id)
                    obj_dict[key] = obj

        return obj_dict

    def new(self, obj):
        """
        Add the object to the current database session.

        Args:
            obj: Object to add to the session.
        """
        if obj:
            self.__session.add(obj)

    def save(self):
        """
        Commit all changes of the current database session.
        """
        self.__session.commit()

    def delete(self, obj=None):
        """
        Delete obj from the current database session.

        Args:
            obj: Object to delete (optional).
        """
        if obj:
            self.__session.delete(obj)

    def reload(self):
        """
        Create all tables and the current database session.
        """
        # Import all models to ensure they are registered with Base
        from models.state import State
        from models.city import City
        from models.user import User
        from models.place import Place
        from models.review import Review
        from models.amenity import Amenity

        # Create all tables
        Base.metadata.create_all(self.__engine)

        # Create session
        session_factory = sessionmaker(bind=self.__engine,
                                       expire_on_commit=False)
        Session = scoped_session(session_factory)
        self.__session = Session()

    def close(self):
        """
        Close the current session.
        """
        self.__session.close()
