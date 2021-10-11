"""
    Defines the Template class, which maintains local templates for testing

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import pathlib
import test.util

from src.blog import Blog

class Template:
    """ Maintains a testing template"""

    def __init__(self, template_name, template_html):
        """ Constructor

            :param template_name: <str> The template's name
            :param template_html: <str> The template HTML
            :return: New object
            """
        self.template_name = pathlib.Path('unittest') / template_name
        self.template_html = template_html
        
    def get(self, blog):
        """ Gets the template

            :param blog: Blog obj under test
            :return: <str> Rendered template HTML
            """
        # Create test client to get template
        config = test.util.load_test_config()
        config['Templates']['Index'] = str(self.template_name)
        blog = Blog(config)

        with blog.app.test_client() as client:
            # Create local HTML file
            template_path = (
                pathlib.Path(blog.app.root_path) /
                blog.app.template_folder /
                self.template_name)

            template_path.parent.mkdir(exist_ok=True)
            
            with template_path.open(mode='w') as f_handle:
                f_handle.write(self.template_html)

            # Return contents and clean up
            try:
                return client.get('/').data
            finally:
                template_path.unlink(missing_ok=True)
                template_path.parent.rmdir()
