#!/usr/bin/python3
"""
Unit tests for DBStorage class.
"""
import unittest
import os
from models.engine.db_storage import DBStorage
from models.state import State
from models.city import City


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db',
                 "DBStorage tests only run with db storage")
class TestDBStorage(unittest.TestCase):
    """
    Test cases for DBStorage class.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.storage = DBStorage()
        self.storage.reload()

    def tearDown(self):
        """
        Tear down test fixtures.
        """
        self.storage.close()

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
        states = self.storage.all(State)
        self.assertIsInstance(states, dict)

    def test_new_method(self):
        """
        Test that new() adds an object to the session.
        """
        state = State(name="TestState")
        self.storage.new(state)
        self.storage.save()
        
        states = self.storage.all(State)
        found = False
        for obj in states.values():
            if obj.name == "TestState":
                found = True
                break
        self.assertTrue(found)

    def test_save_method(self):
        """
        Test that save() commits changes to the database.
        """
        state = State(name="SaveTest")
        self.storage.new(state)
        self.storage.save()
        
        # Reload and check
        self.storage.reload()
        states = self.storage.all(State)
        found = False
        for obj in states.values():
            if obj.name == "SaveTest":
                found = True
                break
        self.assertTrue(found)

    def test_delete_method(self):
        """
        Test that delete() removes an object from the database.
        """
        state = State(name="DeleteTest")
        self.storage.new(state)
        self.storage.save()
        state_id = state.id
        
        self.storage.delete(state)
        self.storage.save()
        
        # Reload and check
        self.storage.reload()
        states = self.storage.all(State)
        found = False
        for obj in states.values():
            if obj.id == state_id:
                found = True
                break
        self.assertFalse(found)

    def test_delete_none(self):
        """
        Test that delete(None) does nothing.
        """
        # Should not raise an error
        self.storage.delete(None)


if __name__ == '__main__':
    unittest.main()
