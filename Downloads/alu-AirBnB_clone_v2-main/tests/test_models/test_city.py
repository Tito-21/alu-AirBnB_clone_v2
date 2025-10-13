#!/usr/bin/python3
"""
Unit tests for City class.
"""
import unittest
import os
from models.city import City
from models.base_model import BaseModel


class TestCity(unittest.TestCase):
    """
    Test cases for City class.
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
        Test that City is properly instantiated.
        """
        city = City()
        self.assertIsInstance(city, City)
        self.assertIsInstance(city, BaseModel)

    def test_attributes(self):
        """
        Test City attributes.
        """
        city = City()
        self.assertTrue(hasattr(city, 'name'))
        self.assertTrue(hasattr(city, 'state_id'))
        self.assertTrue(hasattr(city, 'id'))
        self.assertTrue(hasattr(city, 'created_at'))
        self.assertTrue(hasattr(city, 'updated_at'))

    def test_name_attribute(self):
        """
        Test name attribute can be set.
        """
        city = City()
        city.name = "San Francisco"
        self.assertEqual(city.name, "San Francisco")

    def test_state_id_attribute(self):
        """
        Test state_id attribute can be set.
        """
        city = City()
        city.state_id = "1234"
        self.assertEqual(city.state_id, "1234")

    def test_to_dict(self):
        """
        Test to_dict method includes class name.
        """
        city = City()
        city.name = "Los Angeles"
        city_dict = city.to_dict()
        self.assertEqual(city_dict['__class__'], 'City')
        self.assertEqual(city_dict['name'], 'Los Angeles')


if __name__ == '__main__':
    unittest.main()
