# conftest.py

import mock
import pytest

FILES = {'files': [{'id': 'spam', 'name': 'Spam'}]}

SPREADSHEET = {
    'spreadsheet': {
        'spreadsheetId': 'spam',
        'properties': {'title': 'Spam'},
        'sheets': [
            {'properties': {'title': 'Spam1', 'sheetId': 0, 'index': 0}},
        ],
    },
    'values': {'valueRanges': [{'values': [[1, 2], [3, 4]]}]},
}


@pytest.fixture
def oauth2():
    with mock.patch('gsheets.oauth2.file') as file,\
         mock.patch('gsheets.oauth2.client') as client,\
         mock.patch('gsheets.oauth2.tools') as tools,\
         mock.patch('gsheets.oauth2.argparse') as argparse:
        yield type('oauth2', (object,), locals())


@pytest.fixture
def apiclient():
    services = {'sheets': mock.Mock(), 'drive': mock.Mock()}
    with mock.patch('gsheets.backend.apiclient.discovery.build') as build:
        build.side_effect = lambda serviceName, **kwargs: services[serviceName]
        yield type('apiclient', (object,), services.copy())


@pytest.fixture
def files(request, apiclient):
    files = getattr(request.module, 'FILES', FILES)
    apiclient.drive.files().list().execute.return_value = files
    yield files


@pytest.fixture
def files_all(apiclient, files):
    yield files
    apiclient.drive.files().list.assert_called_with(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        orderBy='folder,name,createdTime', pageToken=None)
    apiclient.drive.files().list().execute.assert_called_with()


@pytest.fixture
def files_name(apiclient, files):
    yield files
    apiclient.drive.files().list.assert_called_with(
        q="name='%s' and mimeType='application/vnd.google-apps.spreadsheet'" % files['files'][0]['name'],
        orderBy='folder,name,createdTime', pageToken=None)
    apiclient.drive.files().list().execute.assert_called_once_with()


@pytest.fixture
def files_name_unknown(apiclient, files):
    apiclient.drive.files().list().execute.return_value = {'files': []}
    yield files
    apiclient.drive.files().list.assert_called_with(
        q="name='%s' and mimeType='application/vnd.google-apps.spreadsheet'" % files['files'][0]['name'],
        orderBy='folder,name,createdTime', pageToken=None)
    apiclient.drive.files().list().execute.assert_called_once_with()


@pytest.fixture
def spreadsheet_404(apiclient):
    from apiclient.errors import HttpError
    http404 = HttpError(resp=mock.Mock(status=404), content=b'')
    apiclient.sheets.spreadsheets().get().execute.side_effect = http404
    yield http404


@pytest.fixture
def spreadsheet(request, apiclient):
    spreadsheet = getattr(request.module, 'SPREADSHEET', SPREADSHEET)
    apiclient.sheets.spreadsheets().get().execute.return_value = spreadsheet['spreadsheet']
    yield spreadsheet
    apiclient.sheets.spreadsheets().get.assert_called_with(
        spreadsheetId=spreadsheet['spreadsheet']['spreadsheetId'])
    apiclient.sheets.spreadsheets().get().execute.assert_called_once_with()


@pytest.fixture
def spreadsheet_values(apiclient, spreadsheet):
    apiclient.sheets.spreadsheets().values().batchGet().execute.return_value = spreadsheet['values']
    yield spreadsheet
    apiclient.sheets.spreadsheets().values().batchGet.assert_called_with(
        spreadsheetId=spreadsheet['spreadsheet']['spreadsheetId'],
        ranges=[s['properties']['title'] for s in spreadsheet['spreadsheet']['sheets']],
        majorDimension='ROWS', valueRenderOption='UNFORMATTED_VALUE')
    apiclient.sheets.spreadsheets().values().batchGet().execute.assert_called_once_with()
