# gsheets - pythonic wrapper for the google sheets api and some drive api

"""Google docs spreadsheets as Python objects."""

from .api import Sheets
from .backend import build_service
from .oauth2 import get_credentials

__all__ = ['Sheets', 'get_credentials', 'build_service']

__title__ = 'gsheets'
__version__ = '0.6.dev0'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE.txt'
__copyright__ = 'Copyright (c) 2016-2021 Sebastian Bank'
