"""
    Defines global settings - to be treated as constants

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""

# Template names
class Template:
    ABOUT = '_about.html'
    BASE = '_index.html'
    ERR_404 = '_404.html'
    POST = '_post.html'

# Path settings
class Route:
    ARCHIVE_URL = 'archive'
    FLASK_ROOT = None
    FLASK_TEMPLATE = 'templates'
    PAGE_URL = 'page'
    POSTS_URL = 'post'

# Renderer settings
class Render:
    BLOG_TITLE = 'Running with Suitcases'
    EMAIL_URL = 'mailto:chris@sprintingwithsuitcases.com'
    GITHUB_URL = 'https://github.com/hughes-ch'
    LINKEDIN_URL = 'https://www.linkedin.com/in/hughes-ch/'
    RENDERED_POST_COUNT = 2
