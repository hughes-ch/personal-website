"""
    Defines unit tests for the static website

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import shutil
import test.util
import unittest
import warnings

from src.blog import Blog
from src.builder import Builder
from src.setting import Settings

class BuilderTest(unittest.TestCase):
    """ Tests the Builder class """

    def setUp(self):
        """ Sets up test case - called each time """
        self.blog = Blog(Settings.instance())
        self.builder = Builder(self.blog.app)

    def tearDown(self):
        """ Cleans up after each test case """
        Settings.destroy()

    def test_links_are_valid(self):
        """ Test that links are valid on static index page """
        shutil.rmtree(self.builder.freezer.root, ignore_errors=True)
        result = test.util.build_static(self.blog.app)
        self.assertEquals(result.exit_code, 0)
        
        app = self.builder.host_static_app()
        with app.test_client() as client:
            response = client.get('/')
            test.util.validate_links(self, client, response.data)

