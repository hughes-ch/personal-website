"""
    Defines the Renderer class, which creates the content for HTML pages

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import jinja2
import math
import pathlib
import pygments
import pygments.formatters
import pygments.lexers
import pygments.util

from .postlist import PostList

class RendererNotConfiguredException(Exception):
    """ Raised when Renderer is not configured """
    pass

class Renderer404Exception(Exception):
    """ Raised when the renderer doesn't know how to make the page  """
    pass

class Renderer:
    """ Creates content for HTML pages """

    def __init__(self, settings):
        """ Constructor

            :param settings: Config file loaded from blog.ini
            :return: New object
            """
        self._app = None
        self._postlist = None
        self._settings = settings

        self._context = {
            'settings': self._settings,
        }

        # Setup parser objects
        self._lang_config = {
            'bash': {
                'lexer': pygments.lexers.BashSessionLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    wrapcode=True)
            },
            'cpp': {
                'lexer': pygments.lexers.CppLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    linenos=True,
                    wrapcode=True)
            },
            'default': {
                'lexer': pygments.lexers.TextLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    wrapcode=True)
            },
            'py': {
                'lexer': pygments.lexers.PythonLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    linenos=True,
                    wrapcode=True)
            },
            'pycon': {
                'lexer': pygments.lexers.PythonConsoleLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    wrapcode=True)
            },
        }
        
    def connect(self, app):
        """ Sets the active flask app

            If config_from_app is True, also takes the configuration
            parameters from the flask app. Note that this copy is a
            shallow copy.

            :param app: Flask application
            :param config_from_app: <Bool> Indicates whether config should
                                           be inherited from app
            :return: None
            """
        self._app = app
        self._postlist = PostList(
            self._settings,
            root_path=app.root_path)

        # Connect context processors
        @self._app.context_processor
        def _connect_context_processors():
            return dict(codeify=self._codeify)

    def render_latest(self, page=1):
        """ Renders the latest blog posts

            :param page: <int> Specifies the page number to render 
            :return: Page contents
            """
        # Verify class is configured correctly
        if not self._is_configured():
            raise RendererNotConfiguredException
            
        # Determine posts on requested page
        posts_per_page = self._find_posts_per_page(
            int(self._settings['Render']['RenderedPostCount']))

        self._context['prev_page'] = None
        self._context['next_page'] = None
        
        if len(posts_per_page) > 0:
            if page < 1 or page > len(posts_per_page):
                return self.render_404()
            else:
                self._context['posts'] = posts_per_page[page-1]

            if page > 1:
                self._context['prev_page'] = page-1
            if page < len(posts_per_page):
                self._context['next_page'] = page+1
            
        else:
            self._context['posts'] = []

            if page != 1:
                return self.render_404()
            
        # Render all posts to template
        return flask.render_template(
            self._settings['Templates']['Index'],
            **self._context)

    def render_404(self):
        """ Renders the 404 page

            :param: None
            :return: 404 status and template
            """
        if not self._is_configured():
            raise RendererNotConfiguredException
        
        return flask.render_template(
            self._settings['Templates']['Err404'],
            **self._context), 404

    def render_post(self, post_name):
        """ Renders single post

            :param post_name: <str> Name of post
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        self._context['post'] = str(
            pathlib.Path('/') / self._settings['Routes']['PostsUrl'] / post_name)

        try:
            return flask.render_template(
                self._settings['Templates']['Post'],
                **self._context)
        except jinja2.exceptions.TemplateNotFound:
            return self.render_404()

    def render_about(self):
        """ Renders the "about" page

            :param: None
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        return flask.render_template(
            self._settings['Templates']['About'],
            **self._context)

    def render_archive(self):
        """ Renders the "archive" page

            :param: None
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        self._context['posts'] = list(self._postlist)

        return flask.render_template(
            self._settings['Templates']['Archive'],
            **self._context)

    def _is_configured(self):
        """ Checks that an instance is configured enough to render a template

            :param: None
            :return: Boolean indicating if instance is configured
            """
        return self._app is not None

    def _codeify(self, code, lang=None):
        """ Escapes, colors, and formats code so the blogger doesn't have to

            :param code: <str> Code to format
            :param lang: <str> Language specifier
            :return: <str> Formatted code
            """
        # Remove leading/trailing whitespace
        is_multiline = '\n' in code
        formatted_code = code.strip()

        # Determine if this is a block or inline piece of code
        if is_multiline:
            formatted_code = self._highlight_syntax(formatted_code, lang)
        else:
            formatted_code = flask.escape(formatted_code)

        # Return clean string as Markup
        return flask.Markup(
            f'<code>{formatted_code}</code>')

    def _find_posts_per_page(self, count):
        """ Finds which posts to render for each page

            :param posts: <list> Of posts
            :param count: <int> Number of posts per page
            :return: <list> Of lists with each index representing a page
            """
        posts_per_page = []

        for idx, post in enumerate(self._postlist):
            mod = idx % count
            if mod == 0:
                posts_per_page.append([])

            posts_per_page[-1].append(str(post.path))

        return posts_per_page

    def _highlight_syntax(self, code, lang):
        """ Modifies code to perform syntax highlighting

            :param code: <str> Code to highlight
            :param lang: <str> Language specifier
            :return: None
            """
        fallback_config = self._lang_config['default']
        return pygments.highlight(
            code,
            self._lang_config.get(lang, fallback_config)['lexer'],
            self._lang_config.get(lang, fallback_config)['formatter'])

