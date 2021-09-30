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

class BuilderTest(unittest.TestCase):
    """ Tests the Builder class """

    def setUp(self):
        """ Sets up test case - called each time """
        config = Blog.get_config()
        self.blog = Blog(config)
        self.builder = Builder(self.blog.app, config)

    def test_links_are_valid(self):
        """ Test that links are valid on static index page """
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.builder.build()
            
        app = self.builder.host_static_app()

        with app.test_client() as client:
            response = client.get('/')
            test.util.validate_links(self, client, response.data)

    def test_empy_build_dir(self):
        """ Test that an empty build directory still results in build """
        shutil.rmtree(self.builder.freezer.root, ignore_errors=True)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.builder.build()
