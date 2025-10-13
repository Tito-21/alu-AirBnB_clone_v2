#!/usr/bin/python3
"""
Unit tests for FileStorage class.
"""
import unittest
import os
from models.engine.file_storage import FileStorage
from models.base_model import BaseModel
from models.state import State
from models.city import City


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                 "FileStorage tests only run with file storage")
class TestFileStorage(unittest.TestCase):
    """
    Test cases for FileStorage class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.storage = FileStorage()

    def tearDown(self):
        """
        Tear down test fixtures.
        """
        try:
            os.remove("file.json")
        except FileNotFoundError:
            pass

    def test_all_returns_dict(self):
        """
        Test that all() returns a dictionary.
        """
        result = self.storage.all()
        self.assertIsInstance(result, dict)

    def test_all_with_class_filter(self):
        """
        Test that all(cls) filters by class.
        """
        state = State()
        state.name = "California"
        self.storage.new(state)

        city = City()
        city.name = "San Francisco"
        self.storage.new(city)

        states = self.storage.all(State)
        self.assertTrue(all(isinstance(obj, State) for obj in states.values()))

    def test_new_method(self):
        """
        Test that new() adds an object to storage.
        """
        obj = BaseModel()
        self.storage.new(obj)
        key = "BaseModel.{}".format(obj.id)
        self.assertIn(key, self.storage.all())

    def test_save_method(self):
        """
        Test that save() creates a file.
        """
        obj = BaseModel()
        self.storage.new(obj)
        self.storage.save()
        self.assertTrue(os.path.exists("file.json"))

    def test_reload_method(self):
        """
        Test that reload() loads objects from file.
        """
        obj = BaseModel()
        obj.name = "Test"
        self.storage.new(obj)
        self.storage.save()

        new_storage = FileStorage()
        new_storage.reload()
        key = "BaseModel.{}".format(obj.id)
        self.assertIn(key, new_storage.all())

    def test_delete_method(self):
        """
        Test that delete() removes an object from storage.
        """
        obj = BaseModel()
        self.storage.new(obj)
        key = "BaseModel.{}".format(obj.id)
        self.assertIn(key, self.storage.all())

        self.storage.delete(obj)
        self.assertNotIn(key, self.storage.all())

    def test_delete_none(self):
        """
        Test that delete(None) does nothing.
        """
        obj = BaseModel()
        self.storage.new(obj)
        all_before = len(self.storage.all())

        self.storage.delete(None)
        all_after = len(self.storage.all())

        self.assertEqual(all_before, all_after)


if __name__ == '__main__':
    unittest.main()
