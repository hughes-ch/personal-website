"""
    Initializes the Blog app

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask_frozen

from .blog import Blog
from .freezer import Freezer

def create_app(test_config=None, frozen=False):
    """ Create and configure blog app """
    config = Blog.get_config()
    blog = Blog(config)

    if frozen:
        freezer = Freezer(blog.app, config)
        freezer.freeze()
        print('--- Static App Ready ---')
        return flask_frozen.Freezer(blog.app).make_static_app()
    else:
        return blog.app
