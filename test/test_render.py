"""
    Defines the TestRender class, which runs a unit test on the Renderer class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import flask
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
        pass
    
    def test_connect(self):
        """ Test the connect method

            :param: None
            :return: None
            """
        # Test that a manually configured renderer is config'd right
        app = flask.Flask(__name__)
        app.config['MY_CONFIG'] = 'config'

        template_name = '_base.html'
        man_config_render = Renderer(template_name)
        man_config_render.connect(app, config_from_app=False)

        self.assertEquals(man_config_render.app, app)
        self.assertEquals(man_config_render.config, {})
        self.assertEquals(man_config_render.root_path, None)
        self.assertEquals(man_config_render.template_folder, None)
        self.assertEquals(man_config_render.base_template, template_name)

        # Test that an automatically configured renderer is config'd right
        auto_config_render = Renderer('_base.html')

        auto_config_render.connect(app, config_from_app=True)

        self.assertEquals(auto_config_render.app, app)
        self.assertEquals(auto_config_render.config, app.config)
        self.assertEquals(auto_config_render.root_path, app.root_path)
        self.assertEquals(auto_config_render.template_folder, app.template_folder)

    def test_renderer_config_check(self):
        """ Test a renderer must be configured to render something

            :param: None
            :return: None
            """
        bad_renderer = Renderer('_base.html')
        with self.assertRaises(RendererNotConfiguredException):
            bad_renderer.render_latest(2, 'url')

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
        response = template.get()
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
        response = template.get()
        self.assertNotIn(b' print', response)
        self.assertNotIn(b'\'', response)

    def test_index_ordering(self):
        """ Test the ordering of the index page

            :param: None
            :return: None
            """
        blog = Blog({'TESTING': True})
        with blog.app.test_client() as client:
            response = client.get('/').data
            
            soup = bs4.BeautifulSoup(response, 'html.parser')
            dates = soup.find_all(id='date')
            datetimes = [datetime.strptime(date.string, '%b %d, %Y')
                         for date in dates]
            
            self.assertEquals(datetimes, sorted(datetimes, reverse=True))
            self.assertEquals(len(datetimes), blog._RENDERED_POST_COUNT)

    def test_render_post(self):
        """ Test how individual posts are rendered

            :param: None
            :return: None
            """
        blog = Blog({'TESTING': True})
        with blog.app.test_client() as client:
            # Find the first link to a blog post in index page
            index_page = client.get('/').data

            index_soup = bs4.BeautifulSoup(index_page, 'html.parser')
            for link in index_soup.find_all('a'):
                if f'/{blog._POSTS_NAME}/' in link['href']:
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
            renderer.render_post('hello', 'post')

    def test_render_post_404(self):
        """ Test how a post is rendered if it is not found

            :param: None
            :return: None
            """
        blog = Blog({'TESTING': True})
        with blog.app.test_client() as client:
            response = client.get(f'/{blog._POSTS_NAME}/not-a-post')
            self.assertEquals(response.status_code, 404)
