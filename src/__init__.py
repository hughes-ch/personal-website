"""
    Initializes the Blog app

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""

import configparser
import pathlib

from .blog import Blog

def create_app(test_config=None):
    """ Create and configure blog app """
    ini_file_path = pathlib.Path(__file__).parent / 'blog.ini'
    
    config = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())
    
    config.read(str(ini_file_path))
    
    blog = Blog(config)
    return blog.app
