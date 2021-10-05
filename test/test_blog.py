"""
    Defines the TestBlog class, which runs a unit test on the Blog class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import os
import pathlib
import requests
import test.util
import unittest

from datetime import date
from parameterized import parameterized
from src.blog import Blog
from src.setting import Settings

class TestBlog(unittest.TestCase):
    """Tests the Blog class"""

    def setUp(self):
        """ Initialize test client

            :param: None
            :return: None
            """
        os.environ['FLASK_APP'] = 'src'
        self.config = test.util.load_test_config()
        self.blog = Blog(self.config)

    def tearDown(self):
        """ Clean up after each test """
        Settings.destroy()

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
        test.util.validate_links(self, self.blog.app.test_client(), response)

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

        test.util.validate_links(self, self.blog.app.test_client(), response.data)

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

    def test_last_page_pagination(self):
        """ Test the pagination button works correctly for the last page

            :param: None
            :return: None
            """
        # The approach to this one is a little hacky. First, update the
        # RenderedPostCount to be well over the amount of posts to get
        # the overall number of posts. Then, update it again so that
        # there are only two blog post pages. Make sure the "Next"
        # button is actually a link.
        self.config = test.util.load_test_config()
        self.config['Render']['RenderedPostCount'] = '2000'
        self.blog = Blog(self.config)
        with self.blog.app.test_client() as client:
            response = client.get('/').data
            soup = bs4.BeautifulSoup(response, 'html.parser')
            all_post_dates = soup.find_all(id='date')
            self.config['Render']['RenderedPostCount'] = str(len(all_post_dates)-1)

        self.blog = Blog(self.config)
        with self.blog.app.test_client() as client:
            response = client.get('/').data
            soup = bs4.BeautifulSoup(response, 'html.parser')
            next_button = soup.find(id='next-nav')
            self.assertIsNotNone(next_button.a)

    def test_static_files(self):
        """ Test serving static files like robots.txt

            :param: None
            :return: None
            """
        with self.blog.app.test_client() as client:
            self.assertEquals(200, client.get('/robots.txt').status_code)

    def test_meta_description(self):
        """ Test the meta description exists

            :param: None
            :return: None
            """
        latest_post_url = test.util.get_latest_url()
        
        with self.blog.app.test_client() as client:
            response = client.get('/').data
            soup = bs4.BeautifulSoup(response, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            self.assertGreater(len(meta_tag['content']), 0)

            response = client.get(latest_post_url).data
            soup = bs4.BeautifulSoup(response, 'html.parser')
            meta_tag = soup.find('meta', attrs={'name':'description'})
            self.assertGreater(len(meta_tag['content']), 0)

    def test_serve_json(self):
        """ Test that JSON is served correctly

            :return: None
            """
        test_cases = [
            ('/', 'Blog'),
            (f'/{self.config["Routes"]["AboutUrl"]}/', 'Person'),
            (f'/{self.config["Routes"]["ArchiveUrl"]}/', 'Blog')
        ]            
        
        for route, schema_type in test_cases:
            with self.blog.app.test_client() as client:
                response = client.get(route).data

                loaded_json = test.util.load_page_json(response)

                self.assertIn(f'"@type": "{schema_type}"', str(response))

                if route == test_cases[0][0]:
                    self.assertIn(b'mainEntity', response)

                    link_attempt_resp = client.get(
                        loaded_json['mainEntity']['url'])
                    self.assertEquals(link_attempt_resp.status_code, 200)

                    # Verify dates can be converted to ISO (no raise)
                    date.fromisoformat(loaded_json['dateCreated'])
                    date.fromisoformat(loaded_json['dateModified'])

                else:
                    self.assertNotIn(b'mainEntity', response)

                if route == test_cases[1][0]:
                    link_attempt_resp = client.get(
                        loaded_json['image'])
                    self.assertEquals(link_attempt_resp.status_code, 200)

                link_attempt_resp = client.get(loaded_json['url'])
                self.assertEquals(link_attempt_resp.status_code, 200)
            
    def test_serve_json_for_post(self):
        """ Test JSON is served correctly for posts

            :return: None
            """
        latest_post_url = pathlib.Path(test.util.get_latest_url())
        
        with self.blog.app.test_client() as client:
            response = client.get(
                f'/{self.config["Routes"]["PostsUrl"]}'
                f'/{latest_post_url.stem}/').data

            loaded_json = test.util.load_page_json(response)

            self.assertIn(f'"@type": "Article"', str(response))
            link_attempt_resp = client.get(loaded_json['url'])
            self.assertEquals(link_attempt_resp.status_code, 200)

            # Verify dates can be converted to ISO (no raise)
            date.fromisoformat(loaded_json['dateCreated'])
            date.fromisoformat(loaded_json['dateModified'])
            date.fromisoformat(loaded_json['datePublished'])

    def test_serve_json_404(self):
        """ Test that JSON is not served for invalid file

            :param: None
            :return: None
            """
        with self.blog.app.test_client() as client:
            response = client.get('/not-real-path/').data

            soup = bs4.BeautifulSoup(response, 'html.parser')
            json_results = soup.find_all('script', type='application/ld+json')

            self.assertEqual(0, len(json_results))

    def test_canonical_links(self):
        """ Tests canonical links in each page type

            :param: None
            :return: None
            """
        input_output_pairs = []

        latest_url = test.util.get_latest_url()
        input_output_pairs.append(
            ('/', f'{self.config["Routes"]["BaseUrl"]}{latest_url}')
        )
        input_output_pairs.append(
            ('/about',
             (f'{self.config["Routes"]["BaseUrl"]}/'
              f'{self.config["Routes"]["AboutUrl"]}/')
            )
        )
        input_output_pairs.append(
            ('/archive',
            (f'{self.config["Routes"]["BaseUrl"]}/'
             f'{self.config["Routes"]["ArchiveUrl"]}/')
            )
        )
        input_output_pairs.append( 
            (latest_url, f'{self.config["Routes"]["BaseUrl"]}{latest_url}')
        )
             
        with self.blog.app.test_client() as client:
            for route, canonical_url in input_output_pairs:
                response = client.get(route).data
                soup = bs4.BeautifulSoup(response, 'html.parser')
                canonical_links = soup.find_all('link', rel='canonical')

                self.assertEqual(len(canonical_links), 1)
                self.assertEqual(canonical_links[0]['href'], canonical_url)
                self.assertEqual(
                    client.get(canonical_links[0]['href']).status_code,
                    200)
