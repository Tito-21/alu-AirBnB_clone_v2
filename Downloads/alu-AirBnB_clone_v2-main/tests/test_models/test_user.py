#!/usr/bin/python3
"""
Unit tests for User class.
"""
import unittest
import os
from models.user import User
from models.base_model import BaseModel


class TestUser(unittest.TestCase):
    """
    Test cases for User class.
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
        Test that User is properly instantiated.
        """
        user = User()
        self.assertIsInstance(user, User)
        self.assertIsInstance(user, BaseModel)

    def test_attributes(self):
        """
        Test User attributes.
        """
        user = User()
        self.assertTrue(hasattr(user, 'email'))
        self.assertTrue(hasattr(user, 'password'))
        self.assertTrue(hasattr(user, 'first_name'))
        self.assertTrue(hasattr(user, 'last_name'))
        self.assertTrue(hasattr(user, 'id'))
        self.assertTrue(hasattr(user, 'created_at'))
        self.assertTrue(hasattr(user, 'updated_at'))

    def test_email_attribute(self):
        """
        Test email attribute can be set.
        """
        user = User()
        user.email = "test@example.com"
        self.assertEqual(user.email, "test@example.com")

    def test_password_attribute(self):
        """
        Test password attribute can be set.
        """
        user = User()
        user.password = "password123"
        self.assertEqual(user.password, "password123")

    def test_to_dict(self):
        """
        Test to_dict method includes class name.
        """
        user = User()
        user.email = "user@test.com"
        user_dict = user.to_dict()
        self.assertEqual(user_dict['__class__'], 'User')
        self.assertEqual(user_dict['email'], 'user@test.com')


if __name__ == '__main__':
    unittest.main()
