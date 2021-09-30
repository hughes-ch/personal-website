"""
    Defines the Builder class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask_frozen
import math
import shutil

from .postlist import PostList

class Builder:
    """ Converts blog to static HTML/CSS """

    def __init__(self, app, settings):
        """ Constructor

            :param app: Flask application
            :param settings: Blog .ini config file contents
            :return: New object
            """
        app.config['FREEZER_DEFAULT_MIMETYPE'] = 'text/html'
        app.config['FREEZER_IGNORE_404_NOT_FOUND'] = True
        app.config['FREEZER_SKIP_EXISTING'] = False
        self.freezer = flask_frozen.Freezer(app)
        self.postlist = PostList(settings, root_path=app.root_path)

        @self.freezer.register_generator
        def index():
            """ Generator for the index method

                :yields: valid index pages
                """
            post_count = len(list(self.postlist))
            num_pages = math.ceil(
                post_count / int(settings['Render']['RenderedPostCount']))

            for page in range(1, num_pages+1):
                yield {'page': page}

        # Freeze blog post pages
        @self.freezer.register_generator
        def blog_post():
            """ Generator for the blog_post method

                :yields: valid blog post pages
                """
            for post in self.postlist:
                yield {'name': post.rel_url}

    def build(self):
        """ Converts blog to static HTML/CSS

            :return: None
            """
        shutil.rmtree(self.freezer.root, ignore_errors=True)
        self.freezer.freeze()

    def host_static_app(self):
        """ Hosts the static application after it is built

            :return: Flask app instance
            """
        return self.freezer.make_static_app()
