"""
    Defines the Builder class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import flask_frozen
import math
import os
import pathlib
import shutil

from .postlist import PostList
from .render import Renderer
from .setting import Settings

class Builder:
    """ Converts blog to static HTML/CSS """

    @staticmethod
    def blog_post():
        """ Generator for the blog_post method

            :yields: valid blog post pages
            """
        for post in PostList(
                Settings.instance(),
                flask.current_app.root_path):
        
            yield {'name': post.rel_url}

    @staticmethod
    def index():
        """ Generator for the index method

            :yields: valid index pages
            """
        post_count = len(
            list(PostList(
                Settings.instance(),
                flask.current_app.root_path)))
        
        num_pages = math.ceil(
            post_count / int(
                Settings.instance()['Render']['RenderedPostCount']))

        for page in range(1, num_pages+1):
            yield {'page': page}

    def __init__(self, app):
        """ Constructor

            :param app: Flask application
            :return: New object
            """
        self.app = app
        self.freezer = flask_frozen.Freezer(app)

        # Register generators
        self.freezer.register_generator(Builder.blog_post)
        self.freezer.register_generator(Builder.index)

    def build(self):
        """ Converts blog to static HTML/CSS

            :return: None
            """
        shutil.rmtree(self.freezer.root, ignore_errors=True)
        self.freezer.freeze()

        # The flask_frozen module doesn't route to the 404 page.
        # Use the renderer to create it for you and copy the
        # results into the build directory.
        renderer = Renderer(Settings.instance())
        renderer.connect(flask.current_app)

        with self.app.test_request_context(base_url=None):
            write_path = pathlib.Path(self.freezer.root) / '404.html'
            with write_path.open('w') as f_handle:
                f_handle.write(renderer.render_404()[0])

    def host_static_app(self):
        """ Hosts the static application after it is built

            :return: Flask app instance
            """
        # Make a new app, hosted from the build area. 
        app = self.freezer.make_static_app()

        # Wrap new app with same settings as one created by Flask
        app.wsgi_app = flask_frozen.script_name_middleware(app.wsgi_app, '')
        self.freezer.init_app(app)
        return app
