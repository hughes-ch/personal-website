"""
    Defines the Renderer class, which creates the content for HTML pages

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask
import inspect
import jinja2
import json
import math
import pathlib
import pygments
import pygments.formatters
import pygments.lexers
import pygments.util

from datetime import datetime
from .postlist import PostList
from .struct_data import StructuredDataFactory

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
            'css': {
                'lexer': pygments.lexers.CssLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    linenos=True,
                    wrapcode=True)
            },
            'default': {
                'lexer': pygments.lexers.TextLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    wrapcode=True)
            },
            'html': {
                'lexer': pygments.lexers.HtmlLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    linenos=True,
                    wrapcode=True)
            },
            'js': {
                'lexer': pygments.lexers.JavascriptLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    linenos=True,
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
            'xml': {
                'lexer': pygments.lexers.XmlLexer(),
                'formatter': pygments.formatters.HtmlFormatter(
                    linenos=True,
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
            return {
                'codeify': self._codeify,
                'settings': self._settings,
                'url': flask.request.url,
            }

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

        context = {
            'title': self._settings['Render']['IndexTitle'],
            'prev_page': None,
            'next_page': None,
        }
        
        if len(posts_per_page) > 0:
            if page < 1 or page > len(posts_per_page):
                return self.render_404()
            else:
                context['posts'] = [
                    flask.Markup(post.contents)
                    for post in posts_per_page[page-1]]

            if page > 1:
                context['prev_page'] = page-1
            if page < len(posts_per_page):
                context['next_page'] = page+1
            
        else:
            context['posts'] = []

            if page != 1:
                return self.render_404()

        # Render SEO content
        try: 
            context['canonical_url'] = f'{posts_per_page[page-1][0].full_url}/'
        except IndexError:
            context['canonical_url'] = f'{self._settings["Routes"]["BaseUrl"]}'

        # Render json
        struct_data_factory = StructuredDataFactory(self._settings)
        context['struct_data'] = struct_data_factory.create_blog(
            self._postlist).as_dict()

        return flask.render_template( 
            self._settings['Templates']['Index'],
            **context)

    def render_404(self):
        """ Renders the 404 page

            :param: None
            :return: 404 status and template
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        context = {
            'title': self._settings['Render']['ErrorTitle']
        }

        return flask.render_template(
            self._settings['Templates']['Err404'],
            **context), 404

    def render_post(self, post_name):
        """ Renders single post

            :param post_name: <str> Name of post
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        # Determine post contents
        try:
            post = self._postlist.get(post_name)

            context = {
                'post': flask.Markup(post.contents),
                'post_description': post.description,
                'title': f'{post.title} - {self._settings["Render"]["BlogTitle"]}',
            }
            
        except ValueError:
            return self.render_404()

        # Render SEO
        context['canonical_url'] = (
            f'{post.full_url}/')

        # Render json
        struct_data_factory = StructuredDataFactory(self._settings)
        context['struct_data'] = struct_data_factory.create_post(
            post).as_dict()

        # Render post
        try:
            return flask.render_template(
                self._settings['Templates']['Post'],
                **context)
        except jinja2.exceptions.TemplateNotFound:
            return self.render_404()

    def render_about(self):
        """ Renders the "about" page

            :param: None
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        context = {
            'title': self._settings['Render']['AboutTitle'],
            'canonical_url': (
                f'{self._settings["Routes"]["BaseUrl"]}/'
                f'{self._settings["Routes"]["AboutUrl"]}/'),
        }
        
        # Render json
        struct_data_factory = StructuredDataFactory(self._settings)
        context['struct_data'] = struct_data_factory.create_about().as_dict()

        return flask.render_template(
            self._settings['Templates']['About'],
            **context)

    def render_archive(self):
        """ Renders the "archive" page

            :param: None
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        context = {
            'posts': list(self._postlist),
            'title': self._settings['Render']['ArchiveTitle'],
            'canonical_url': (
                f'{self._settings["Routes"]["BaseUrl"]}/'
                f'{self._settings["Routes"]["ArchiveUrl"]}/'),
        }

        # Render json
        struct_data_factory = StructuredDataFactory(self._settings)
        context['struct_data'] = struct_data_factory.create_archive(
            self._postlist).as_dict()

        return flask.render_template(
            self._settings['Templates']['Archive'],
            **context)

    def render_feed(self):
        """ Renders the RSS feed

            :param: None
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        postlist = list(self._postlist)

        context = {
            'last_pub_date': postlist[0].date_rfc822,
            'posts': postlist,
        }

        return flask.render_template(
            self._settings['Templates']['Feed'],
            **context)

    def render_feed_style(self):
        """ Renders the RSS feed stylesheet

            Note that this includes contact info at the bottom so it has to
            be a template and not a static file...

            :param: None
            :return: Page contents
            """
        if not self._is_configured():
            raise RendererNotConfiguredException

        return flask.render_template(self._settings['Templates']['FeedXsl'])

    def render_sitemap(self):
        """ Renders the sitemap

            :param: None
            :return: Page contents
            """
        context = {
            'urls': [],
        }

        dateFormat = '%Y-%m-%d'
        context['urls'].append({
            'loc': (f'{self._settings["Routes"]["BaseUrl"]}/'
                  f'{self._settings["Routes"]["AboutUrl"]}'),
            'lastmod': datetime.today().strftime(dateFormat),
        })
        for post in self._postlist:
            loc = post.full_url
            lastmod = post.date.strftime(dateFormat)
            context['urls'].append({
                'loc': loc,
                'lastmod': lastmod,
            })

        return flask.render_template(
            self._settings['Templates']['Sitemap'],
            **context)

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
            code_class = ''
        else:
            formatted_code = flask.escape(formatted_code)
            code_class = 'class="inline"'

        # Return clean string as Markup
        return flask.Markup(
            f'<code {code_class}>{formatted_code}</code>')

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

            posts_per_page[-1].append(post)

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
