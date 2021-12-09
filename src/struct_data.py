"""
    Defines the classes to build structured data for SEO

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import json

from datetime import datetime

# Constants
SCHEMA_CONTEXT = 'https://schema.org'

# Class definitions
class StructuredDataThing:
    """ Represents a simple "Thing" """

    def __init__(self, thing):
        """ Constructor

            :param: <StructuredDataX> to convert to thing
            :return: New instance
            """
        self._thing = thing

    def as_dict(self):
        """ Converts this thing into a dict

            :return: Dict representation of object
            """
        return {
            '@context': SCHEMA_CONTEXT,
            '@type': 'Thing',
            'description': self._thing['description'],
            'name': self._thing['name'],
            'url': self._thing['url'],
        }
    
class StructuredDataAuthor:
    """ Represents an author in structured data """

    def __init__(self, settings):
        """ Constructor

            :param settings: Blog settings from .ini
            :return: New instance
            """
        self._settings = settings

    def __str__(self):
        """ Returns a string representation of the author in JSON

            :return: <str> JSON string
            """
        return json.dumps(self.as_dict())

    def as_dict(self):
        """ Returns a dict representation of the author

            :return: <dict> Representation of author
            """
        return {
            '@context': SCHEMA_CONTEXT,
            '@type': 'Person',
            'description': self._settings['Struct']['AuthorDescription'],
            'email': self._settings['Struct']['AuthorEmail'],
            'image': self._settings['Struct']['AuthorImage'],
            'jobTitle': self._settings['Struct']['AuthorJobTitle'],
            'name': self._settings['Struct']['AuthorName'],
            'telephone': self._settings['Struct']['AuthorTelephone'],
            'url': (f'{self._settings["Struct"]["BaseUrl"]}/'
                    f'{self._settings["Routes"]["AboutUrl"]}')
        }

class StructuredDataBlogPost:
    """ Represents a single blog post in structured data """

    def __init__(self,  post=None, author=None, settings=None):
        """ Constructor

            :param post: <Post> From the PostList
            :param author: <StructuredDataAuthor> for author of blog
            :param settings: Taken from blog .ini file
            """
        if post is None or author is None or settings is None:
            raise ValueError

        self._post = post
        self._author = author
        self._settings = settings

    def __str__(self):
        """ Creates a string representation of a blog post in JSON

            :return: <str> Representation of a blog post in JSON
            """
        return json.dumps(self.as_dict())

    def as_dict(self):
        """ Returns a dict representation of a blog post

            :return: <dict> Representation of blog post
            """
        return {
            '@context': SCHEMA_CONTEXT,
            '@type': 'Article',
            'articlebody': self._post.contents.replace('\n', '\\n'),
            'author': self._author.as_dict(),
            'dateCreated': self._post.date.strftime('%Y-%m-%d'),
            'dateModified': self._post.mod_date.strftime('%Y-%m-%d'),
            'datePublished': self._post.date.strftime('%Y-%m-%d'),
            'description': self._post.description,
            'headline': self._post.title,
            'name': self._post.title,
            'url': (f'{self._settings["Struct"]["BaseUrl"]}'
                    f'{self._post.rel_url}')
        }

class StructuredDataBlog:
    """ Represents a full blog in structured data """ 

    def __init__(self,
                 postlist=None, author=None,
                 settings=None, has_main_entity=True):
        """ Constructor

            :param postlist: <PostList> populated with all blog posts
            :param author: <StructuredDataAuthor> for author of blog
            :param settings: Taken from blog .ini file
            :param has_main_entity: <Bool> Indicating if there's a main post 
            """
        if postlist is None or author is None or settings is None:
            raise ValueError

        self._postlist = postlist
        self._author = author
        self._settings = settings
        self._has_main_entity = has_main_entity

    def __str__(self):
        """ Creates a string representation of object in JSON

            :return: <str> Representing object in JSON
            """
        return json.dumps(self.as_dict())

    def as_dict(self):
        """ Returns a dict representation of a blog 

            :return: <dict> Representation of blog 
            """
        blog_data = {
            '@context': SCHEMA_CONTEXT,
            '@type': 'Blog',
            'blogPost': [],
            'author': self._author.as_dict(),
            'dateCreated': self._settings['Struct']['BlogDateCreated'],
            'dateModified': list(self._postlist)[0].mod_date.strftime('%Y-%m-%d'),
            'description': self._settings['Render']['BlogDescription'],
            'name': self._settings['Render']['BlogTitle'],
            'url': f'{self._settings["Struct"]["BaseUrl"]}/',
        }

        for idx, post in enumerate(self._postlist):
            if idx >= int(self._settings['Render']['RenderedPostCount']):
                break
            
            struct_post = StructuredDataBlogPost(
                post=post,
                author=self._author,
                settings=self._settings)

            blog_data['blogPost'].append(struct_post.as_dict())

        if self._has_main_entity:
            blog_data['mainEntity'] = StructuredDataThing(
                blog_data['blogPost'][0]).as_dict()

        return blog_data
        
class StructuredDataFactory:
    """ Holds common build settings and constructs objects """

    def __init__(self, settings):
        """ Constructor

            :param settings: Application config from .ini
            :return: New instance
            """
        if settings is None:
            raise ValueError

        self._settings = settings

    def create_blog(self, postlist):
        """ Creates an object representing struct data for blog

            :param post_list: <PostList> with all posts
            :return: <StructuredDataBlog>
            """
        return StructuredDataBlog(
            postlist=postlist,
            author=StructuredDataAuthor(self._settings),
            settings=self._settings)

    def create_archive(self, postlist):
        """ Creates an object representing struct data for the archive page

            :param post_list: <PostList> with all posts
            :return: <StructuredDataBlog>
            """
        return StructuredDataBlog(
            postlist=postlist,
            author=StructuredDataAuthor(self._settings),
            settings=self._settings,
            has_main_entity=False)

    def create_about(self):
        """ Creates an object representing struct data for the about page

            :return: <StructuredDataAuthor>
            """
        return StructuredDataAuthor(self._settings)

    def create_post(self, post):
        """ Creates an object representing struct data for a single post

            :param post: <Post> from the PostList
            :return: <StructuredDataBlogPost>
            """
        return StructuredDataBlogPost(
            post=post,
            author=StructuredDataAuthor(self._settings),
            settings=self._settings)
