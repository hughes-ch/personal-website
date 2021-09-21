"""
    Defines testing utilities

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import configparser
import pathlib

def load_test_config():
    """ Loads a generic test configuration

        :param: None
        :return: Config from INI modified to be in a test config
        """
    ini_file_path = pathlib.Path(__file__).parent / 'blog.ini'
    config = configparser.ConfigParser()
    config.read(str(ini_file_path))
    config['Flask']['Testing'] = 'True'

    return config
