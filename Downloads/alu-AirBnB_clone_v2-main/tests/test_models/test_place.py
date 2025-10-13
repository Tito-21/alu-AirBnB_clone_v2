#!/usr/bin/python3
"""
Unit tests for Place class.
"""
import unittest
import os
from models.place import Place
from models.base_model import BaseModel


class TestPlace(unittest.TestCase):
    """
    Test cases for Place class.
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
        Test that Place is properly instantiated.
        """
        place = Place()
        self.assertIsInstance(place, Place)
        self.assertIsInstance(place, BaseModel)

    def test_attributes(self):
        """
        Test Place attributes.
        """
        place = Place()
        self.assertTrue(hasattr(place, 'city_id'))
        self.assertTrue(hasattr(place, 'user_id'))
        self.assertTrue(hasattr(place, 'name'))
        self.assertTrue(hasattr(place, 'description'))
        self.assertTrue(hasattr(place, 'number_rooms'))
        self.assertTrue(hasattr(place, 'number_bathrooms'))
        self.assertTrue(hasattr(place, 'max_guest'))
        self.assertTrue(hasattr(place, 'price_by_night'))
        self.assertTrue(hasattr(place, 'latitude'))
        self.assertTrue(hasattr(place, 'longitude'))

    def test_name_attribute(self):
        """
        Test name attribute can be set.
        """
        place = Place()
        place.name = "My House"
        self.assertEqual(place.name, "My House")

    def test_number_rooms_default(self):
        """
        Test number_rooms default value.
        """
        place = Place()
        place.number_rooms = 4
        self.assertEqual(place.number_rooms, 4)

    def test_to_dict(self):
        """
        Test to_dict method includes class name.
        """
        place = Place()
        place.name = "Beautiful Place"
        place_dict = place.to_dict()
        self.assertEqual(place_dict['__class__'], 'Place')
        self.assertEqual(place_dict['name'], 'Beautiful Place')


if __name__ == '__main__':
    unittest.main()
