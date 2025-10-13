#!/usr/bin/python3
"""
Unit tests for Amenity class.
"""
import unittest
import os
from models.amenity import Amenity
from models.base_model import BaseModel


class TestAmenity(unittest.TestCase):
    """
    Test cases for Amenity class.
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
        Test that Amenity is properly instantiated.
        """
        amenity = Amenity()
        self.assertIsInstance(amenity, Amenity)
        self.assertIsInstance(amenity, BaseModel)

    def test_attributes(self):
        """
        Test Amenity attributes.
        """
        amenity = Amenity()
        self.assertTrue(hasattr(amenity, 'name'))
        self.assertTrue(hasattr(amenity, 'id'))
        self.assertTrue(hasattr(amenity, 'created_at'))
        self.assertTrue(hasattr(amenity, 'updated_at'))

    def test_name_attribute(self):
        """
        Test name attribute can be set.
        """
        amenity = Amenity()
        amenity.name = "WiFi"
        self.assertEqual(amenity.name, "WiFi")

    def test_to_dict(self):
        """
        Test to_dict method includes class name.
        """
        amenity = Amenity()
        amenity.name = "Pool"
        amenity_dict = amenity.to_dict()
        self.assertEqual(amenity_dict['__class__'], 'Amenity')
        self.assertEqual(amenity_dict['name'], 'Pool')


if __name__ == '__main__':
    unittest.main()
