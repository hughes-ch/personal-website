"""
    Initializes the Blog app

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask_frozen

from .blog import Blog
from .builder import Builder

def create_app(test_config=None, is_hosting_static=False):
    """ Create and configure blog app """
    config = Blog.get_config()
    blog = Blog(config)

    if is_hosting_static:
        builder = Builder(blog.app, config)
        builder.build()
        print('--- Static App Ready ---')
        return builder.host_static_app()
    else:
        return blog.app
