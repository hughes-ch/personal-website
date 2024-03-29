"""
    Defines the Blog class, which creates and maintains Flask app.

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import pathlib

from .render import Renderer
from . import cli

class Blog:
    """ Creates and maintains the Flask app """

    def __init__(self, settings):
        """ Constructor
        
            Routes each URL to a class method

            :param settings_file: <str> Name of INI file
            :return: New instance
            """
        # Create and configure flask instance
        self.app = flask.Flask(__name__)
        self.app.config.update(**settings['Flask'])
        self.app.url_map.strict_slashes = False

        # Add CLI commands
        self.app.cli.add_command(cli.build)
        self.app.cli.add_command(cli.run_static)
        
        # Create renderer object
        self.renderer = Renderer(settings)
        self.renderer.connect(self.app)

        # Create index page
        @self.app.route('/')
        @self.app.route(f'/{settings["Routes"]["PageUrl"]}/<int:page>/')
        def index(page=1):
            """ Creates the index page with latest blog posts

                :param page: <int> Page number
                :return: Page content
                """
            return self.renderer.render_latest(page=page)
        
        # Create about page
        @self.app.route(f'/{settings["Routes"]["AboutUrl"]}/')
        def about():
            return self.renderer.render_about()

        # Create archive page
        @self.app.route(f'/{settings["Routes"]["ArchiveUrl"]}/')
        def archive():
            return self.renderer.render_archive()
 
        # Create individual post pages
        @self.app.route(f'/{settings["Routes"]["PostsUrl"]}/<name>/')
        def blog_post(name=None):
            """ Creates an individual post page

                :param name: <str> Page number
                :return: Page content
                """
            return self.renderer.render_post(name)

        # Handle 404
        @self.app.errorhandler(404)
        def page_not_found(err):
            """ Renders the 404 page

                :param err: The encountered error
                :return: Page content
                """
            return self.renderer.render_404()

        # Serve robots.txt
        robots = 'robots.txt'
        @self.app.route(f'/{robots}')
        def serve_robots():
            """ Serves robots.txt

                :param: None
                :return: Page content
                """
            return flask.send_from_directory(
                pathlib.Path(self.app.static_folder) /
                settings['Routes']['RobotsLocation'],
                robots)

        # Serve RSS feed
        @self.app.route(f'/{settings["Routes"]["RssFeed"]}')
        def serve_rss():
            """ Serves RSS feed

                :param: None
                :return: Page content
                """
            return self.serve_xml(self.renderer.render_feed)

        # Serve style for RSS feed
        @self.app.route(f'/{settings["Routes"]["RssFeedXsl"]}')
        def serve_rss_style():
            """ Serves RSS feed stylesheet

                :param: None
                :return: Page content
                """
            return self.serve_xml(self.renderer.render_feed_style)

        # Serve sitemap
        @self.app.route(f'/{settings["Routes"]["Sitemap"]}')
        def serve_sitemap():
            """ Serves the sitemap

                :param: None
                :return: Page content
                """
            return self.serve_xml(self.renderer.render_sitemap)
        
    def serve_xml(self, render_func):
        """ Serves an XML route

            :param render_func: Function handle that defines how to serve route
            :return: Page content
            """
        xml_content = render_func()
        response = flask.make_response(xml_content)
        response.headers['Content-Type'] = 'application/xml'
        return response
