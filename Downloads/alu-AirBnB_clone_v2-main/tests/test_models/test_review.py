#!/usr/bin/python3
"""
Unit tests for Review class.
"""
import unittest
import os
from models.review import Review
from models.base_model import BaseModel


class TestReview(unittest.TestCase):
    """
    Test cases for Review class.
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
        Test that Review is properly instantiated.
        """
        review = Review()
        self.assertIsInstance(review, Review)
        self.assertIsInstance(review, BaseModel)

    def test_attributes(self):
        """
        Test Review attributes.
        """
        review = Review()
        self.assertTrue(hasattr(review, 'place_id'))
        self.assertTrue(hasattr(review, 'user_id'))
        self.assertTrue(hasattr(review, 'text'))
        self.assertTrue(hasattr(review, 'id'))
        self.assertTrue(hasattr(review, 'created_at'))
        self.assertTrue(hasattr(review, 'updated_at'))

    def test_text_attribute(self):
        """
        Test text attribute can be set.
        """
        review = Review()
        review.text = "Great place!"
        self.assertEqual(review.text, "Great place!")

    def test_to_dict(self):
        """
        Test to_dict method includes class name.
        """
        review = Review()
        review.text = "Amazing experience"
        review_dict = review.to_dict()
        self.assertEqual(review_dict['__class__'], 'Review')
        self.assertEqual(review_dict['text'], 'Amazing experience')


if __name__ == '__main__':
    unittest.main()
