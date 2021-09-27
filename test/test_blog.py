"""
    Defines the TestBlog class, which runs a unit test on the Blog class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import pathlib
import requests
import test.util
import unittest

from src.blog import Blog

class TestBlog(unittest.TestCase):
    """Tests the Blog class"""

    def setUp(self):
        """ Initialize test client

            :param: None
            :return: None
            """
        self.config = test.util.load_test_config()
        self.blog = Blog(self.config)

    def get_index_page(self):
        """ Returns the contents of the index page

            :param: None
            :return: Contents of index (if valid response received)
            """
        with self.blog.app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            return response

    def test_index_response(self):
        """ Verify index page returns latest blog posts

            :param: None
            :return: None
            """
        response = self.get_index_page()
        posts_dir_name = self.config['Routes']['PostsUrl']
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
        """ Verify internal links return a valid response

            :param: None
            :return: None
            """
        response = self.get_index_page().data
        test.util.validate_links(self, response)

    def test_index_pagination(self):
        """ Test the pagination feature of the main index page

            :param: None
            :return: None
            """
        # Request first page and verify it matches index page
        page_url = self.config['Routes']['PageUrl']

        with self.blog.app.test_client() as client:
            index_data = client.get('/').data
            page1_response = client.get(f'/{page_url}/1')
            self.assertEqual(index_data, page1_response.data)
            self.assertEqual(page1_response.status_code, 200)

            # Request following pages and verify they differ from last
            max_page_count = 5000
            last_page_content = page1_response.data
            
            for page_num in range(max_page_count):
                next_page_response = client.get(f'/{page_url}/{page_num}')
                self.assertIn(next_page_response.status_code, [200, 404])
                self.assertNotEqual(last_page_content, next_page_response.data)

                if next_page_response.status_code == 404:
                    break

            self.assertNotEqual(page_num, max_page_count)

    def test_index_pagination_incorrect_page(self):
        """ Verify an incorrect page number is handled correctly

            :param: None
            :return: None
            """
        # Request first page and verify it matches index page
        page_url = self.config['Routes']['PageUrl']

        with self.blog.app.test_client() as client:
            status_code = client.get(f'/{page_url}/0').status_code
            self.assertEqual(status_code, 404)

            status_code = client.get(f'/{page_url}/5000').status_code
            self.assertEqual(status_code, 404)

    def test_about_page(self):
        """ Tests the about page is rendered

            :param: None
            :return: None
            """
        about_url = self.config['Routes']['AboutUrl']
        
        with self.blog.app.test_client() as client:
            status_code = client.get(f'/{about_url}').status_code
            self.assertEqual(status_code, 200)

    def test_404(self):
        """ Tests the 404 page

            :param: None
            :return: None
            """
        with self.blog.app.test_client() as client:
            response = client.get('/not-a-page')
            self.assertEquals(response.status_code, 404)

        test.util.validate_links(self, response.data)

    def test_render_all_posts(self):
        """ Test when RenderedPostCount > amount of posts

            :param: None
            :return: None
            """
        self.config = test.util.load_test_config()
        old_post_count = self.config['Render']['RenderedPostCount']
        self.config['Render']['RenderedPostCount'] = '2000'
        self.blog = Blog(self.config)

        with self.blog.app.test_client() as client:
            response = client.get('/')
            self.assertEquals(response.status_code, 200)

            soup = bs4.BeautifulSoup(response.data, 'html.parser')
            all_post_dates = soup.find_all(id='date')
            self.assertGreater(len(all_post_dates), int(old_post_count))
        
        
            
