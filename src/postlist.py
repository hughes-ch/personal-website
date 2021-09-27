"""
    Defines the PostList class, which maintains a list of posts

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import collections
import pathlib

from datetime import datetime

class Post:
    """ Contains data for a single post """

    def __init__(self, post_path):
        """ Constructor

            :param post_path: <Path> to template HTML
            :return: New instance
            """
        self.rel_url = post_path.stem
        self.path = pathlib.Path('/') / post_path.parent.stem / self.rel_url

        with post_path.open() as f_handle:
            html = f_handle.read()
            soup = bs4.BeautifulSoup(html, 'html.parser')

            # Find the date of the post
            try:
                date_str = soup.find(id="date").string
                post_date = datetime.strptime(
                    date_str,
                    '%b %d, %Y')

            except (AttributeError, ValueError):
                post_date = datetime.now()

            self.date = post_date
            self.datestr = self.date.strftime('%b %d, %Y')

            # Find the title of the post
            self.title = soup.find('h3').string

class PostList:
    """ Maintains the date, title, path, etc of blog posts """

    def __init__(self, settings, root_path='/'):
        """ Constructor

            :param root_path: <str> Path to app root directory
            :return: New instance
            """
        self._posts = None
        self._root_path = root_path
        self._settings = settings

    def __iter__(self):
        """ Returns an iterator. Loads posts if not done already

            :param: None
            :return: Iterator
            """
        self._load_posts()
        return iter(self._posts.values())

    def get(self, url):
        """ Gets the post at the requested URL

            :param url: <str> URL of given post
            :return: <Post> or raises ValueError
            """
        self._load_posts()
        try:
            return self._posts[url]
        except KeyError:
            raise ValueError

    def _load_posts(self):
        """ Loads the post information if not done already

            :param: None
            :return: None
            """
        if self._posts is None:
            post_list = []

            post_path = (pathlib.Path(self._root_path) /
                self._settings['Routes']['FlaskTemplate'] /
                self._settings['Routes']['PostsUrl'])

            for path in post_path.glob('*.html'):
                post_list.append(Post(path))

            sorted_post_list = sorted(
                post_list,
                key=lambda entry: entry.date,
                reverse=True)

            self._posts = collections.OrderedDict(
                [(post.rel_url, post) for post in sorted_post_list])

            
