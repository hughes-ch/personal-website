"""
    Defines the Renderer class, which creates the content for HTML pages

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import flask
import jinja2
import math
import pathlib

from datetime import datetime
from .setting import BlogSetting

class RendererNotConfiguredException(Exception):
    """ Raised when Renderer is not configured """
    pass

class Renderer404Exception(Exception):
    """ Raised when the renderer doesn't know how to make the page  """
    pass

class Renderer:
    """ Creates content for HTML pages """

    def __init__(self,
                 params,
                 base_template='_base.html',
                 err404_template='_404.html',
                 post_template='_post.html'):
        """ Constructor

            :param params: <dict> Specifying constants of website
            :param base_template: <str> Name of base template
            :param err404_template: <str> Name of 404 template
            :param post_template: <str> Name of post template
            :return: New object
            """
        self._RENDERED_POST_COUNT = 2
        self.app = None
        self.base_template = base_template
        self.config = {}
        self.err404_template = err404_template
        self.post_template = post_template
        self.root_path = None
        self.template_folder = None

        self.context = {
            'params': params,
            'BlogSetting': BlogSetting,
        }
        
    def connect(self, app, config_from_app=False):
        """ Sets the active flask app

            If config_from_app is True, also takes the configuration
            parameters from the flask app. Note that this copy is a
            shallow copy.

            :param app: Flask application
            :param config_from_app: <Bool> Indicates whether config should
                                           be inherited from app
            :return: None
            """
        # Set configuration parameters
        self.app = app

        if config_from_app:
            self.config = self.app.config.copy()
            self.root_path = self.app.root_path
            self.template_folder = self.app.template_folder

        # Connect context processors
        @self.app.context_processor
        def _connect_context_processors():
            return dict(codeify=self._codeify)

    def render_latest(self, count, post_url, page=1):
        """ Renders the latest blog posts

            :param count: <int> Number of posts to render
            :param post_url: <str> Base URL of blog posts
            :param page: <int> Specifies the page number to render 
            :return: Page contents
            """
        # Verify class is configured correctly
        if not self._is_configured():
            raise RendererNotConfiguredException
            
        # Get list of latest posts
        posts_path = (
            pathlib.Path(self.root_path) /
            self.template_folder /
            post_url)

        posts = self._find_latest_posts(posts_path)

        # Determine posts on requested page
        posts_per_page = self._find_posts_per_page(posts, count)

        self.context['prev_page'] = None
        self.context['next_page'] = None
        
        if len(posts_per_page) > 0:
            if page < 1 or page >= len(posts_per_page):
                return self.render_404()
            else:
                self.context['posts'] = posts_per_page[page-1]

            if page > 1:
                self.context['prev_page'] = page-1
            if page < len(posts_per_page)-1:
                self.context['next_page'] = page+1
            
        else:
            self.context['posts'] = []

            if page != 1:
                return self.render_404()
            
        # Render all posts to template
        return flask.render_template(self.base_template, **self.context)

    def render_404(self):
        """ Renders the 404 page

            :param: None
            :return: 404 status and template
            """
        if not self._is_configured():
            raise RendererNotConfiguredException
        
        return flask.render_template(self.err404_template), 404

    def render_post(self, post_name, post_dir_name):
        """ Renders single post

            :param post_name: <str> Name of post
            :param post_dir_name: <str> Name of post dir
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        self.context['post'] = str(
            pathlib.Path('/') / post_dir_name / post_name)

        try:
            return flask.render_template(self.post_template, **self.context)
        except jinja2.exceptions.TemplateNotFound:
            return self.render_404()

    def _is_configured(self):
        """ Checks that an instance is configured enough to render a template

            :param: None
            :return: Boolean indicating if instance is configured
            """
        return (self.app is not None and
                self.root_path is not None and
                self.template_folder is not None)

    def _codeify(self, code):
        """ Escapes, colors, and formats code so the blogger doesn't have to

            :param code: <str> Code to format
            :return: <str> Formatted code
            """
        # Determine if this is a block or inline piece of code
        class_statement = ''
        pre_open = ''
        pre_close = ''
        
        if '\n' in code:
            class_statement = 'class="code-block"'
            pre_open = '<pre>'
            pre_close = '</pre>'

        # Remove leading/trailing whitespace
        formatted_code = code.strip()

        # Return clean string as Markup
        return flask.Markup(
            f'{pre_open}<code {class_statement}>%s</code>{pre_close}') % formatted_code

    def _find_latest_posts(self, post_path):
        """ Returns the latest posts in sorted order

            :param path: <PosixPath> Path to posts on filesystem
            :return: <list> Of sorted post titles
            """
        # Find date of each post
        post_list = []
        for path in post_path.glob('*.html'):
            with path.open() as f_handle:
                html = f_handle.read()
                soup = bs4.BeautifulSoup(html, 'html.parser')

                try:
                    date_str = soup.find(id="date").string
                    post_date = datetime.strptime(
                        date_str,
                        '%b %d, %Y')
                    
                except (AttributeError, ValueError):
                    post_date = datetime.now()
                    
            post_list.append(
                {
                    'path': pathlib.Path('/') / post_path.stem / path.stem,
                    'date': post_date
                }
            )

        # Return posts in sorted order
        posts = [
            str(post['path']) for post in sorted(
                post_list,
                key=lambda entry: entry['date'],
                reverse=True
            )
        ]

        return posts

    def _find_posts_per_page(self, posts, count):
        """ Finds which posts to render for each page

            :param posts: <list> Of posts
            :param count: <int> Number of posts per page
            :return: <list> Of lists with each index representing a page
            """
        posts_per_page = []

        for idx, post in enumerate(posts):
            mod = idx % count
            if mod == 0:
                posts_per_page.append([])

            posts_per_page[-1].append(post)

        return posts_per_page
