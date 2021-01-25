# auth.py - do oauth2

"""Helpers for doing OAuth 2.0 authentification."""

import os

from oauth2client import file, client, tools

from .tools import doctemplate

__all__ = ['get_credentials']

SCOPES = 'read'

SECRETS = '~/client_secrets.json'

STORAGE = '~/storage.json'


@doctemplate(SCOPES, SECRETS, STORAGE)
def get_credentials(scopes=None, secrets=None, storage=None, *,
                    no_webserver=False):
    """Make OAuth 2.0 credentials for scopes from ``secrets`` and ``storage`` files.

    Args:
        scopes: scope URL(s) or ``'read'``, ``'write'`` (default: ``%r``)
        secrets: location of secrets file (default: ``%r``)
        storage: location of storage file (default: ``%r``)
        no_webserver: url/code prompt instead of webbrowser based auth

    see https://developers.google.com/sheets/quickstart/python
    see https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """
    scopes = Scopes.get(scopes)

    if secrets is None:
        secrets = SECRETS
    if storage is None:
        storage = STORAGE

    secrets, storage = map(os.path.expanduser, (secrets, storage))

    store = file.Storage(storage)
    creds = store.get()

    if creds is None or creds.invalid:
        flow = client.flow_from_clientsecrets(secrets, scopes)
        args = ['--noauth_local_webserver'] if no_webserver else []
        flags = tools.argparser.parse_args(args)
        creds = tools.run_flow(flow, store, flags)

    return creds


class Scopes(object):
    """URLs for read or read/write access to Google sheets and drive.

    see https://developers.google.com/sheets/guides/authorizing

    >>> Scopes.get('read')  # doctest: +NORMALIZE_WHITESPACE
    ('https://www.googleapis.com/auth/spreadsheets.readonly',
     'https://www.googleapis.com/auth/drive.readonly')

    >>> Scopes.get('write')  # doctest: +NORMALIZE_WHITESPACE
    ('https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive')

    >>> Scopes.get('spam')
    'spam'

    >>> Scopes.get(('spam', 'eggs'))
    ('spam', 'eggs')

    >>> assert Scopes.get() == Scopes.get('read')
    """

    read = r = (
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
    )

    write = rw = (
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    )

    _keywords = {'read', 'r', 'write', 'rw'}

    default = SCOPES

    @classmethod
    def get(cls, scope=None):
        """Return default or predefined URLs from keyword, pass through ``scope``."""
        if scope is None:
            scope = cls.default
        if isinstance(scope, str) and scope in cls._keywords:
            return getattr(cls, scope)
        return scope
