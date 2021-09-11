"""
    Defines the Template class, which maintains local templates for testing

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import pathlib

from src.blog import Blog

class Template:
    """ Maintains a testing template"""

    def __init__(self, template_name, template_html):
        """ Constructor

            :param template_name: <str> The template's name
            :param template_html: <str> The template HTML
            :return: New object
            """
        self.template_name = template_name
        self.template_html = template_html
        self.root_path = pathlib.Path(__file__).parent.absolute()

    def get(self):
        """ Gets the template

            :param: None
            :return: <str> Rendered template HTML
            """
        # Create test client to get template
        with Blog(base_template=self.template_name,
                  root_path=self.root_path,
                  template_path=self.root_path).app.test_client() as client:

            # Create local HTML file
            template_path = pathlib.Path(self.root_path) / self.template_name
            with template_path.open(mode='w') as f_handle:
                f_handle.write(self.template_html)

            # Return contents and clean up
            try:
                return client.get('/').data
            finally:
                template_path.unlink(missing_ok=True)
