"""
    Defines the Blog class, which creates and maintains Flask app.

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask

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
            return flask.render_template('_base.html')

