"""
    Defines unit tests for PostList

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import concurrent.futures
import test.util
import time
import unittest
import unittest.mock as mock

from src.postlist import PostList
from src.setting import Settings

class TestPostList(unittest.TestCase):
    """ Defines unit tests for the PostList class """

    def test_load_post_called_once(self):
        """ Test that the _load_posts method is only called once

            :return: None
            """
        postlist = PostList(None)

        # Mock the load method to take a while
        def slow_load():
            time.sleep(5)
            postlist._posts = []
        
        postlist._load_posts = mock.Mock(side_effect=slow_load)

        num_threads = 3
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=num_threads) as executor:
            for ii in range(num_threads):
                executor.submit(postlist._check_configure)

        postlist._load_posts.assert_called_once()

    def test_load_description(self):
        """ Test that descriptions are loaded correctly """

        blog = test.util.create_blog()

        with blog.app.test_request_context():
            postlist = PostList(Settings.instance(), blog.app.root_path)

            for post in postlist:
                self.assertNotIn('\n', post.description)
                self.assertNotEqual(' ', post.description[0])
                self.assertNotIn('  ', post.description)

    def test_load_title(self):
        """ Test that titles are loaded without newlines or special chars """
        blog = test.util.create_blog()

        with blog.app.test_request_context():
            postlist = PostList(Settings.instance(), blog.app.root_path)

            for post in postlist:
                self.assertNotIn('\n', post.title)
                self.assertNotEqual(' ', post.title[0])
                self.assertNotIn(r'&#39', post.title)
