"""
    Defines the TestBlog class, which runs a unit test on the Blog class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import pathlib
import requests
import unittest

from bs4 import BeautifulSoup
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

    def get_index_page(self):
        """ Returns the contents of the index page

            :param: None
            :return: Contents of index (if valid response received)
            """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        return response

    def test_index_response(self):
        """ Verify index page returns latest blog posts

            :param: None
            :return: None
            """
        response = self.get_index_page()
        posts_dir_name = self.blog._POSTS_NAME
        posts_full_path = (
            pathlib.Path(self.blog.app.root_path) /
            self.blog.app.template_folder /
            posts_dir_name)

        posts = [path.stem for path in posts_full_path.glob('*.html')]

        found_a_recent_post = False
        for post in posts:
            if post in str(response.data):
                found_a_recent_post = True
                break

        self.assertTrue(found_a_recent_post)

    def test_links_are_valid(self):
        """ Verifies internal links return a valid response

            :param: None
            :return: None
            """
        bad_status_codes = [400, 404, 408, 410, 421, 501, 502, 503, 504]

        # Find all links on page
        response = self.get_index_page()
        soup = BeautifulSoup(response.data, 'html.parser')
        for a in soup.find_all('a'):
            href = a.get('href')
            if 'http' in href:
                # Do not send external requests during development...
                #response = requests.head(href)
                pass
            elif 'mailto' in href:
                pass
            else:
                response = self.client.get(href)

            self.assertNotIn(
                response.status_code,
                bad_status_codes,
                msg=f'{response.status_code} returned by "{href}"')
                
