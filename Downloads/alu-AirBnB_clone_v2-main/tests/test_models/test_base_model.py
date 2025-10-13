#!/usr/bin/python3
"""
Unit tests for BaseModel class.
"""
import unittest
import os
import time
from datetime import datetime
from models.base_model import BaseModel
from models import storage


class TestBaseModel(unittest.TestCase):
    """
    Test cases for BaseModel class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        pass

    def tearDown(self):
        """
        Tear down test fixtures.
        """
        try:
            os.remove("file.json")
        except FileNotFoundError:
            pass

    def test_instantiation(self):
        """
        Test that BaseModel is properly instantiated.
        """
        obj = BaseModel()
        self.assertIsInstance(obj, BaseModel)
        self.assertIsInstance(obj.id, str)
        self.assertIsInstance(obj.created_at, datetime)
        self.assertIsInstance(obj.updated_at, datetime)

    def test_unique_id(self):
        """
        Test that each instance has a unique id.
        """
        obj1 = BaseModel()
        obj2 = BaseModel()
        self.assertNotEqual(obj1.id, obj2.id)

    def test_str_representation(self):
        """
        Test the string representation of BaseModel.
        """
        obj = BaseModel()
        string = str(obj)
        self.assertIn("[BaseModel]", string)
        self.assertIn(obj.id, string)

    def test_save_method(self):
        """
        Test the save method updates updated_at.
        """
        obj = BaseModel()
        old_updated_at = obj.updated_at
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        obj.save()
        self.assertNotEqual(old_updated_at, obj.updated_at)

    def test_to_dict_method(self):
        """
        Test the to_dict method returns a dictionary.
        """
        obj = BaseModel()
        obj_dict = obj.to_dict()
        self.assertIsInstance(obj_dict, dict)
        self.assertEqual(obj_dict['__class__'], 'BaseModel')
        self.assertEqual(obj_dict['id'], obj.id)
        self.assertIsInstance(obj_dict['created_at'], str)
        self.assertIsInstance(obj_dict['updated_at'], str)

    def test_to_dict_no_sa_instance_state(self):
        """
        Test that to_dict does not include _sa_instance_state.
        """
        obj = BaseModel()
        obj._sa_instance_state = "test"
        obj_dict = obj.to_dict()
        self.assertNotIn('_sa_instance_state', obj_dict)

    def test_kwargs_instantiation(self):
        """
        Test instantiation with kwargs.
        """
        obj = BaseModel()
        obj.name = "Test"
        obj.number = 42
        obj_dict = obj.to_dict()
        new_obj = BaseModel(**obj_dict)
        self.assertEqual(new_obj.id, obj.id)
        self.assertEqual(new_obj.name, obj.name)
        self.assertEqual(new_obj.number, obj.number)
        self.assertIsInstance(new_obj.created_at, datetime)
        self.assertIsInstance(new_obj.updated_at, datetime)

    def test_delete_method(self):
        """
        Test the delete method.
        """
        obj = BaseModel()
        obj.save()
        obj_id = obj.id
        obj.delete()
        storage.save()
        all_objs = storage.all()
        key = "BaseModel.{}".format(obj_id)
        self.assertNotIn(key, all_objs)


if __name__ == '__main__':
    unittest.main()
