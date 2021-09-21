"""
    Defines the Blog class, which creates and maintains Flask app.

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
from .render import Renderer

import flask
import pathlib

class Blog:
    """ Creates and maintains the Flask app """

    def __init__(self, settings):
        """ Constructor
        
            Routes each URL to a class method

            :param settings_file: <str> Name of INI file
            :return: New instance
            """
        # Create and configure flask instance
        self.app = flask.Flask(
            __name__,
            root_path=settings['Routes'].get('FlaskRoot', None),
            template_folder=settings['Routes']['FlaskTemplate'])

        self.app.config.from_mapping(settings['Flask'])

        # Create renderer object
        self.renderer = Renderer(settings)
        self.renderer.connect(self.app)

        # Create index page
        @self.app.route('/')
        @self.app.route(f'/{settings["Routes"]["PageUrl"]}/<int:page>')
        def index(page=1):
            """ Creates the index page with latest blog posts

                :param page: <int> Page number
                :return: Page content
                """
            return self.renderer.render_latest(page=page)
        
        # Create about page
        @self.app.route(f'/{settings["Routes"]["AboutUrl"]}')
        def about():
            return self.renderer.render_about()

        # Create archive page
        @self.app.route(f'/{settings["Routes"]["ArchiveUrl"]}')
        @self.app.route(f'/{settings["Routes"]["ArchiveUrl"]}/<int:page>')
        def archive(page=1):
            return 'Not Implemented'

        # Create individual post pages
        @self.app.route(f'/{settings["Routes"]["PostsUrl"]}/<name>')
        def blog_post(name=None):
            """ Creates an individual post page

                :param name: <str> Page number
                :return: Page content
                """
            return self.renderer.render_post(name)

