# conftest.py

import oauth2client
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
def open_(mocker):
    yield mocker.patch('builtins.open', mocker.mock_open())


@pytest.fixture
def pandas(mocker):
    def read_csv(fd, **kwargs):
        kwargs = dict(fd_getvalue=fd.getvalue(), **kwargs)
        return mocker.NonCallableMock(kwargs=kwargs)
    yield mocker.patch('gsheets.export.pandas', autospec=True,
                       **{'read_csv.side_effect': read_csv})


@pytest.fixture
def oauth2(mocker):
    module = mocker.create_autospec(oauth2client, name='oauth2client')
    mocker.patch.multiple('gsheets.oauth2', file=module.file,
                          client=module.client, tools=module.tools)

    yield module


@pytest.fixture
def services(mocker):
    services = {s: mocker.NonCallableMock(name=s) for s in ['sheets', 'drive']}
    mocker.patch('apiclient.discovery.build', autospec=True,
                 side_effect=lambda serviceName, **kwargs: services[serviceName])

    yield mocker.NonCallableMock(name='services', **services)


@pytest.fixture
def files(request, services):
    files = getattr(request.module, 'FILES', FILES)
    services.drive.files.return_value.list.return_value.execute.return_value = files

    yield files


@pytest.fixture
def files_name(services, files):
    yield files

    list_ = services.drive.files.return_value.list
    name = files['files'][0]['name']
    list_.assert_called_once_with(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'",
        orderBy='folder,name,createdTime',
        pageToken=None)
    list_.return_value.execute.assert_called_once_with()


@pytest.fixture
def files_name_unknown(services, files):
    list_ = services.drive.files.return_value.list
    list_.return_value.execute.return_value = {'files': []}

    yield files

    name = files['files'][0]['name']
    list_.assert_called_once_with(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'",
        orderBy='folder,name,createdTime',
        pageToken=None)
    list_.return_value.execute.assert_called_once_with()


@pytest.fixture
def spreadsheet_404(mocker, services):
    from apiclient.errors import HttpError
    http404 = HttpError(resp=mocker.NonCallableMock(status=404), content=b'')
    services.sheets.spreadsheets.return_value.get.return_value.execute.side_effect = http404

    yield http404


@pytest.fixture
def spreadsheet(request, services):
    spreadsheet = getattr(request.module, 'SPREADSHEET', SPREADSHEET)
    get = services.sheets.spreadsheets.return_value.get
    get.return_value.execute.return_value = spreadsheet['spreadsheet']

    yield spreadsheet

    get.assert_called_once_with(
        spreadsheetId=spreadsheet['spreadsheet']['spreadsheetId'])
    get.return_value.execute.assert_called_once_with()


@pytest.fixture
def spreadsheet_values(services, spreadsheet):
    batchGet = services.sheets.spreadsheets.return_value.values.return_value.batchGet  # noqa: N806
    batchGet.return_value.execute.return_value = spreadsheet['values']

    yield spreadsheet

    batchGet.assert_called_once_with(
        spreadsheetId=spreadsheet['spreadsheet']['spreadsheetId'],
        ranges=[s['properties']['title'] for s in spreadsheet['spreadsheet']['sheets']],
        majorDimension='ROWS',
        valueRenderOption='UNFORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING')
    batchGet.return_value.execute.assert_called_once_with()
