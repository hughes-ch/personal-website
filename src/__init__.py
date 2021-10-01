"""
    Initializes the Blog app

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import flask_frozen

from .blog import Blog
from .builder import Builder
from .setting import Settings

def create_app():
    """ Create and configure blog app """
    config = Settings.instance()
    blog = Blog(config)
    return blog.app

