# backend.py - talk to the sheets and drive api with google-api-client-python

"""Thin wrappers around apiclient method calls."""

import apiclient

from ._compat import iteritems

__all__ = ['build_service', 'iterfiles', 'spreadsheet', 'values']

SERVICES = {
    'sheets': {'serviceName': 'sheets', 'version': 'v4'},
    'drive': {'serviceName': 'drive', 'version': 'v3'},
}

SHEET = 'application/vnd.google-apps.spreadsheet'

FILEORDER = 'folder,name,createdTime'


def build_service(name=None, **kwargs):
    """Return a service endpoint for interacting with a Google API."""
    if name is not None:
        for kw, value in iteritems(SERVICES[name]):
            kwargs.setdefault(kw, value)
    return apiclient.discovery.build(**kwargs)


def iterfiles(service, name=None, mimeType=SHEET, order=FILEORDER):
    """Fetch and yield (id, name) pairs for Google drive files."""
    params = {'orderBy': order, 'pageToken': None}
    q = []
    if name is not None:
        q.append("name='%s'" % name)
    if mimeType is not None:
        q.append("mimeType='%s'" % mimeType)
    if q:
        params['q'] = ' and '.join(q)

    while True:
        response = service.files().list(**params).execute()
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
    params = {'majorDimension': 'ROWS', 'valueRenderOption': 'UNFORMATTED_VALUE'}
    params.update(spreadsheetId=id, ranges=ranges)
    response = service.spreadsheets().values().batchGet(**params).execute()
    return response['valueRanges']
