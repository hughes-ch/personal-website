"""
    Defines unit tests for the frozen website

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask_frozen
import test.util
import unittest
import warnings

from src.blog import Blog
from src.freezer import Freezer

class FreezerTest(unittest.TestCase):
    """ Tests the Freezer class """

    def setUp(self):
        """ Sets up the test case - executed each time

            :param: None
            :return: None
            """
        config = Blog.get_config()
        blog = Blog(config)

        freezer = Freezer(blog.app, config)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            freezer.freeze()
            
        self.app = flask_frozen.Freezer(blog.app).make_static_app()

    def test_links_are_valid(self):
        """ Test that links are valid on static index page """
        with self.app.test_client() as client:
            response = client.get('/')
            test.util.validate_links(self, client, response.data)

