"""
    Defines the TestRender class, which runs a unit test on the Renderer class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import flask
import test.util
import unittest

from datetime import datetime
from src.blog import Blog
from src.render import Renderer
from src.render import RendererNotConfiguredException
from test.template import Template

class TestRenderer(unittest.TestCase):
    """Tests the Renderer class"""

    def setUp(self):
        """ Initialize test client

            :param: None
            :return: None
            """
        self.config = test.util.load_test_config()
        self.blog = Blog(self.config)
    
    def test_renderer_config_check(self):
        """ Test a renderer must be configured to render something

            :param: None
            :return: None
            """
        bad_renderer = Renderer(self.config)
        with self.assertRaises(RendererNotConfiguredException):
            bad_renderer.render_latest()

    def test_codeify(self):
        """ Test a block of code rendered with _codeify

            :param: None
            :return: None
            """
        # Create Template
        template_name = 'test.html'
        template_html = """
            <!DOCTYPE html>
              <html>
                <head>
                </head>
                <body>
                  {{ codeify("
                     print('hello world!')
                  ") }}
                </body>
              </html>
        """ 

        # Verify it was rendered correctly
        template = Template(template_name, template_html)
        response = template.get(self.blog)
        self.assertIn(b'code-block', response)
        self.assertIn(b'<pre>', response)
        self.assertIn(b'</pre>', response)
        self.assertNotIn(b' print', response)
        self.assertNotIn(b'\'', response)

    def test_inline_codeify(self):
        """ Test an inline span of code rendered with _codeify

            :param: None
            :return: None
            """
        # Create template
        template_name = 'test.html'
        template_html = """
            <!DOCTYPE html>
              <html>
                <head>
                </head>
                <body>
                  {{ codeify("print('hello world!')") }}
                </body>
              </html>
        """
        
        # Verify it was rendered correctly
        template = Template(template_name, template_html)
        response = template.get(self.blog)
        self.assertNotIn(b' print', response)
        self.assertNotIn(b'\'', response)

    def test_index_ordering(self):
        """ Test the ordering of the index page

            :param: None
            :return: None
            """
        with self.blog.app.test_client() as client:
            response = client.get('/').data
            
            soup = bs4.BeautifulSoup(response, 'html.parser')
            dates = soup.find_all(id='date')
            datetimes = [datetime.strptime(date.string, '%b %d, %Y')
                         for date in dates]
            
            self.assertEquals(datetimes, sorted(datetimes, reverse=True))
            self.assertEquals(
                len(datetimes),
                int(self.config['Render']['RenderedPostCount']))

    def test_render_post(self):
        """ Test how individual posts are rendered

            :param: None
            :return: None
            """
        with self.blog.app.test_client() as client:
            # Find the first link to a blog post in index page
            index_page = client.get('/').data

            index_soup = bs4.BeautifulSoup(index_page, 'html.parser')
            for link in index_soup.find_all('a'):
                if f'/{self.config["Routes"]["PostsUrl"]}/' in link['href']:
                    # Verify post is returned successfully 
                    response = client.get(link['href'])
                    self.assertEquals(response.status_code, 200)

                    # Verify post looks correct by checking for 'date' id
                    post_soup = bs4.BeautifulSoup(response.data, 'html.parser')
                    self.assertNotEqual(len(post_soup.find_all(id='date')), 0)

    def test_render_post_not_configured(self):
        """ Test how a post is rendered if renderer not configured

            :param: None
            :return: None
            """
        renderer = Renderer(None)
        with self.assertRaises(RendererNotConfiguredException):
            renderer.render_post('hello')

    def test_render_post_404(self):
        """ Test how a post is rendered if it is not found

            :param: None
            :return: None
            """
        with self.blog.app.test_client() as client:
            response = client.get(
                f'/{self.config["Routes"]["PostsUrl"]}/not-a-post')
            
            self.assertEquals(response.status_code, 404)

    def test_render_about_not_configured(self):
        """ Test that the about page cannot be rendered if not configured

            :param: None
            :return: None
            """
        renderer = Renderer(None)
        with self.assertRaises(RendererNotConfiguredException):
            renderer.render_about()
