#!/usr/bin/python3
"""
Unit tests for State class.
"""
import unittest
import os
from models.state import State
from models.base_model import BaseModel


class TestState(unittest.TestCase):
    """
    Test cases for State class.
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
        Test that State is properly instantiated.
        """
        state = State()
        self.assertIsInstance(state, State)
        self.assertIsInstance(state, BaseModel)

    def test_attributes(self):
        """
        Test State attributes.
        """
        state = State()
        self.assertTrue(hasattr(state, 'name'))
        self.assertTrue(hasattr(state, 'id'))
        self.assertTrue(hasattr(state, 'created_at'))
        self.assertTrue(hasattr(state, 'updated_at'))

    def test_name_attribute(self):
        """
        Test name attribute can be set.
        """
        state = State()
        state.name = "California"
        self.assertEqual(state.name, "California")

    def test_to_dict(self):
        """
        Test to_dict method includes class name.
        """
        state = State()
        state.name = "Nevada"
        state_dict = state.to_dict()
        self.assertEqual(state_dict['__class__'], 'State')
        self.assertEqual(state_dict['name'], 'Nevada')


if __name__ == '__main__':
    unittest.main()
