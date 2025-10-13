#!/usr/bin/python3
"""
This module defines the FileStorage class for file-based storage.
"""
import json
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class FileStorage:
    """
    FileStorage class for serializing instances to a JSON file
    and deserializing JSON file to instances.

    Attributes:
        __file_path (str): Path to the JSON file.
        __objects (dict): Dictionary storing all objects.
    """
    __file_path = "file.json"
    __objects = {}

    def all(self, cls=None):
        """
        Return the dictionary __objects or filtered by class.

        Args:
            cls: Class to filter by (optional).

        Returns:
            dict: Dictionary of objects.
        """
        if cls:
            filtered_dict = {}
            for key, value in self.__objects.items():
                if isinstance(value, cls):
                    filtered_dict[key] = value
                elif isinstance(cls, str) and key.startswith(cls + '.'):
                    filtered_dict[key] = value
                elif hasattr(cls, '__name__') and key.startswith(
                        cls.__name__ + '.'):
                    filtered_dict[key] = value
            return filtered_dict
        return self.__objects

    def new(self, obj):
        """
        Set in __objects the obj with key <obj class name>.id.

        Args:
            obj: Object to add to __objects.
        """
        if obj:
            key = "{}.{}".format(obj.__class__.__name__, obj.id)
            self.__objects[key] = obj

    def save(self):
        """
        Serialize __objects to the JSON file.
        """
        obj_dict = {}
        for key, value in self.__objects.items():
            obj_dict[key] = value.to_dict()

        with open(self.__file_path, 'w', encoding='utf-8') as f:
            json.dump(obj_dict, f)

    def reload(self):
        """
        Deserialize the JSON file to __objects.
        """
        try:
            with open(self.__file_path, 'r', encoding='utf-8') as f:
                obj_dict = json.load(f)

            for key, value in obj_dict.items():
                class_name = value['__class__']
                del value['__class__']
                self.__objects[key] = eval(class_name)(**value)
        except FileNotFoundError:
            pass

    def delete(self, obj=None):
        """
        Delete obj from __objects if it's inside.

        Args:
            obj: Object to delete (optional).
        """
        if obj:
            key = "{}.{}".format(obj.__class__.__name__, obj.id)
            if key in self.__objects:
                del self.__objects[key]

    def close(self):
        """
        Call reload() method for deserializing the JSON file to objects.
        """
        self.reload()
