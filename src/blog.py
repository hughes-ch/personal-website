"""
    Defines the Blog class, which creates and maintains Flask app.

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import pathlib

class Blog:
    """ Creates and maintains the Flask app """

    def __init__(self, config=None):
        """ Constructor
        
            Routes each URL to a class method

            :param: None
            :return: New instance
            """
        # Create and configure flask instance
        self.app = flask.Flask(__name__)
        self.app.config['POSTS_URL'] = 'post'
        self.app.config['POSTS_DIR'] = (
            pathlib.Path(self.app.root_path) /
            self.app.template_folder /
            self.app.config['POSTS_URL'])

        if config is not None:
            self.app.config.from_mapping(config)

        # Create index page
        @self.app.route('/')
        def index():
            # Find active posts
            posts = [str(pathlib.Path(self.app.config['POSTS_URL']) / path.stem)
                     for path in self.app.config['POSTS_DIR'].glob('*.html')]

            # Render all posts to template
            return flask.render_template('_base.html', posts=posts)

        # Create about page
        @self.app.route('/about')
        def about():
            return 'Not Implemented'

        # Create archive page
        self._ARCHIVE_NAME = 'archive'
        @self.app.route(f'/{self._ARCHIVE_NAME}')
        @self.app.route(f'/{self._ARCHIVE_NAME}/<int:page>')
        def archive(page=1):
            return 'Not Implemented'

        # Create individual post pages
        @self.app.route('/post/<name>')
        def blog_post(name=None):
            return 'Not Implemented'

