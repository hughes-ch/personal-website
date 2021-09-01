from .blog import Blog

def create_app(test_config=None):
    """ Create and configure blog app """
    blog = Blog()
    return blog.app
