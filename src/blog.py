"""
    Defines the Blog class, which creates and maintains Flask app.

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import pathlib

class Blog:
    """ Creates and maintains the Flask app """

    def __init__(self):
        """ Constructor
        
            Routes each URL to a class method

            :param: None
            :return: New instance
            """
        # Create and configure flask instance
        self.app = flask.Flask(__name__)

        # Create index page
        @self.app.route('/')
        def index():
            # Find active posts
            posts_dir_name = 'posts'
            posts_full_path = (
                pathlib.Path(self.app.root_path) /
                self.app.template_folder /
                posts_dir_name)

            posts = [str(pathlib.Path(posts_dir_name) / path.name)
                     for path in posts_full_path.glob('operator-overloading*.html')]
            
            # Render all posts to template
            return flask.render_template('_base.html', posts=posts)

