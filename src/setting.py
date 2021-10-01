"""
    Defines the Settings class

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import configparser
import pathlib

class Settings:
    """ Maintains the settings for this app """
    _instance = None

    @staticmethod
    def instance():
        """ Returns instance. Creates one if not already created.
        
            :return: Settings instance
            """
        if Settings._instance is None:
            ini_file_path = pathlib.Path(__file__).parent / 'blog.ini'
    
            Settings._instance = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation())
    
            Settings._instance.read(str(ini_file_path))
            
        return Settings._instance

    @staticmethod
    def destroy():
        """ Destroy the instance """
        Settings._instance = None
