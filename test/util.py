"""
    Defines testing utilities

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import bs4
import configparser
import pathlib

from src.blog import Blog

def load_test_config():
    """ Loads a generic test configuration

        :param: None
        :return: Config from INI modified to be in a test config
        """
    ini_file_path = pathlib.Path(__file__).parent / 'blog.ini'
    config = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation())
    config.read(str(ini_file_path))
    config['Flask']['Testing'] = 'True'

    return config

def create_blog():
    """ Creates a Blog

        :param: None
        :return: Blog object
        """
    config = load_test_config()
    return Blog(config)

def validate_links(context, html):
    """ Validates all links on page

        :param context: Unit test context (self)
        :param html: <str> HTML response from client
        :return: None
        """
    bad_status_codes = [400, 404, 408, 410, 421, 501, 502, 503, 504]

    # Find all links on page
    soup = bs4.BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a'):
        href = a.get('href')
        if 'http' in href:
            # Do not send external requests during development...
            #response = requests.head(href)
            pass
        elif 'mailto' in href:
            pass
        else:
            with create_blog().app.test_client() as client:
                response = client.get(href)

        context.assertNotIn(
            response.status_code,
            bad_status_codes,
            msg=f'{response.status_code} returned by "{href}"')

def get_latest_url():
    """ Finds the latest blog post URL

        :param: None
        :return: <str> Representing latest blog post URL
        """
    config = load_test_config()

    with Blog(config).app.test_client() as client:
        response = client.get('/').data
        soup = bs4.BeautifulSoup(response, 'html.parser')
        links = soup.find_all('a')
        
        for link in links:
            if config['Routes']['PostsUrl'] in link['href']:
                return link['href']
