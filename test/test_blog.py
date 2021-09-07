"""
    Defines the TestBlog class, which runs a unit test on the Blog class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import pathlib
import unittest

from src.blog import Blog

class TestBlog(unittest.TestCase):
    """Tests the Blog class"""

    def setUp(self):
        """ Initialize test client

            :param: None
            :return: None
            """
        self.blog = Blog({'TESTING': True})
        self.client = self.blog.app.test_client()

    def test_index_response(self):
        """ Verify index page returns latest blog posts

            :param: None
            :return: None
            """
        # Verify status code
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Find latest blog posts within response
        posts_dir_name = self.blog.app.config['POSTS_DIR']
        posts_full_path = (
            pathlib.Path(self.blog.app.root_path) /
            self.blog.app.template_folder /
            posts_dir_name)

        posts = [path.stem for path in posts_full_path.glob('*.html')]

        for post in posts:
            self.assertIn(post, str(response.data))
