"""
    Defines the CLI 

    :copyright: Copyright (c) 2021 Chris Hughes
    :license: MIT License. See LICENSE.md for details
"""
import click
import flask
import flask.cli
import os

from .builder import Builder

@click.command('build')
@flask.cli.with_appcontext
def build():
    """ Builds static HTML files from the flask app

        :return: None
        """
    builder = Builder(flask.current_app)
    builder.build()

@click.command('run-static')
@click.argument('host')
@flask.cli.with_appcontext
def run_static(host):
    """ Serve the static version of the website

        :return: None
        """
    builder = Builder(flask.current_app)
    app = builder.host_static_app()

    # The FLASK_RUN_FROM_CLI environment variable needs to be set
    # to prevent duplicate calls to start the werkzeug server. In
    # this case, since this is being called from a CLI, the server
    # isn't being called anyways. It's safe to set the environment
    # back to false and call app.run. Otherwise, would have to
    # start the server directly with the werkzeug API. 
    os.environ['FLASK_RUN_FROM_CLI'] = 'false'
    app.run(host=host)

