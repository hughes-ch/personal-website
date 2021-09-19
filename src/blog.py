"""
    Defines the Blog class, which creates and maintains Flask app.

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
from .render import Renderer
from .setting import BlogSetting

import flask
import pathlib

class Blog:
    """ Creates and maintains the Flask app """

    def __init__(self,
                 config=None,
                 base_template='_index.html',
                 err404_template='_404.html',
                 post_template='_post.html',
                 root_path=None, template_path='templates'):
        """ Constructor
        
            Routes each URL to a class method

            :param config: <dict> Flask config
            :param base_template: <str> Name of template for index page
            :param err404_template: <str> Name of template for 404 page
            :param post_temlate: <str> Name of template for indiv post page
            :param root_path: <str> Path to flask root
            :param template_path: <str> Path to flask templates
            :return: New instance
            """
        # Create and configure flask instance
        self.app = flask.Flask(
            __name__,
            root_path=root_path,
            template_folder=template_path)
        
        if config is not None:
            self.app.config.from_mapping(config)

        # Create renderer object
        self._RENDERED_POST_COUNT = 2

        self._params = {}
        self._params[BlogSetting.TITLE] = (
            'Running with Suitcases')
        self._params[BlogSetting.LINKEDIN] = (
            'https://www.linkedin.com/in/hughes-ch/')
        self._params[BlogSetting.GITHUB] = (
            'https://github.com/hughes-ch')
        self._params[BlogSetting.EMAIL] = (
            'mailto:chris@sprintingwithsuitcases.com')

        self.renderer = Renderer(
            self._params,
            base_template,
            err404_template,
            post_template)
        
        self.renderer.connect(self.app, config_from_app=True)

        # Create URL constants
        self._ARCHIVE_NAME = 'archive'
        self._PAGE_NAME = 'page'
        self._POSTS_NAME = 'post'

        # Create index page
        @self.app.route('/')
        @self.app.route(f'/{self._PAGE_NAME}/<int:page>')
        def index(page=1):
            """ Creates the index page with latest blog posts

                :param page: <int> Page number
                :return: Page content
                """
            return self.renderer.render_latest(
                self._RENDERED_POST_COUNT,
                self._POSTS_NAME,
                page=page)
        
        # Create about page
        @self.app.route('/about')
        def about():
            return 'Not Implemented'

        # Create archive page
        @self.app.route(f'/{self._ARCHIVE_NAME}')
        @self.app.route(f'/{self._ARCHIVE_NAME}/<int:page>')
        def archive(page=1):
            return 'Not Implemented'

        # Create individual post pages
        @self.app.route(f'/{self._POSTS_NAME}/<name>')
        def blog_post(name=None):
            """ Creates an individual post page

                :param name: <str> Page number
                :return: Page content
                """
            return self.renderer.render_post(
                name,
                self._POSTS_NAME)

