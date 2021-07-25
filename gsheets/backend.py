"""Thin wrappers around google-api-client-python talking to sheets/drive API."""

import re

import apiclient

__all__ = ['build_service',
           'iterfiles',
           'spreadsheet',
           'values'
           'quote']

SERVICES = {'sheets': {'serviceName': 'sheets', 'version': 'v4'},
            'drive': {'serviceName': 'drive', 'version': 'v3'}}

SHEET = 'application/vnd.google-apps.spreadsheet'

FILEORDER = 'folder,name,createdTime'

IS_ALPHANUMERIC_A1 = re.compile(r'[a-zA-Z]{1,3}'  # last column 'ZZZ' (18_278)
                                r'\d{1,}').fullmatch


def build_service(name=None, **kwargs):
    """Return a service endpoint for interacting with a Google API."""
    if name is not None:
        for kw, value in SERVICES[name].items():
            kwargs.setdefault(kw, value)
    if 'cache_discovery' not in kwargs:
        try:
            from oauth2client import __version__ as o2c_version
        except ImportError:  # pragma: no cover
            pass
        else:
            # ImportError: file_cache is unavailable when using oauth2client >= 4.0.0 or google-auth
            if o2c_version == '4' or o2c_version.startswith('4.'):
                kwargs['cache_discovery'] = False

    return apiclient.discovery.build(**kwargs)


def iterfiles(service, *, name=None, mimeType=SHEET, order=FILEORDER):  # noqa: N803
    """Fetch and yield ``(id, name)`` pairs for Google drive files."""
    params = {'orderBy': order, 'pageToken': None}
    q = []
    if name is not None:
        q.append(f"name='{name}'")
    if mimeType is not None:
        q.append(f"mimeType='{mimeType}'")
    if q:
        params['q'] = ' and '.join(q)

    while True:
        request = service.files().list(**params)
        response = request.execute()
        for f in response['files']:
            yield f['id'], f['name']
        try:
            params['pageToken'] = response['nextPageToken']
        except KeyError:
            return


def spreadsheet(service, id):
    """Fetch and return spreadsheet meta data with Google sheets API."""
    request = service.spreadsheets().get(spreadsheetId=id)
    try:
        response = request.execute()
    except apiclient.errors.HttpError as e:
        if e.resp.status == 404:
            raise KeyError(id)
        else:  # pragma: no cover
            raise
    return response


def values(service, id, ranges):
    """Fetch and return spreadsheet cell values with Google sheets API."""
    params = {'majorDimension': 'ROWS',
              'valueRenderOption': 'UNFORMATTED_VALUE',
              'dateTimeRenderOption': 'FORMATTED_STRING',
              'spreadsheetId': id,
              'ranges': ranges}
    request = service.spreadsheets().values().batchGet(**params)
    response = request.execute()
    return response['valueRanges']


def quote(worksheet_name: str) -> str:
    """Return ``worksheet_name``, single-quote if needed.

    >>> quote('spam')
    'spam'

    >>> quote('spam spam')
    'spam spam'

    >>> quote('DKC3')
    "'DKC3'"
    """
    if IS_ALPHANUMERIC_A1(worksheet_name):
        # https://developers.google.com/sheets/api/guides/concepts#expandable-1
        return f"'{worksheet_name}'"
    return worksheet_name
