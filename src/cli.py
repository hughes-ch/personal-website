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
from .setting import Settings

@click.command('build')
@flask.cli.with_appcontext
def build():
    """ Builds static HTML files for deployment

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
    os.environ['FLASK_RUN_FROM_CLI'] = 'false'
    builder = Builder(flask.current_app)
    app = builder.host_static_app(host)

