# test_api.py

import pytest

import gsheets


@pytest.fixture
def sheets(mocker):
    return gsheets.Sheets(credentials=mocker.sentinel.credentials)


def test_from_files(oauth2):
    oauth2.file.Storage.return_value.get.return_value = None

    sheets = gsheets.Sheets.from_files()

    oauth2.client.flow_from_clientsecrets.assert_called_once()
    oauth2.tools.run_flow.assert_called_once_with(
        oauth2.client.flow_from_clientsecrets.return_value,
        oauth2.file.Storage.return_value,
        oauth2.tools.argparser.parse_args.return_value)
    assert isinstance(sheets, gsheets.Sheets)
    assert sheets._creds is oauth2.tools.run_flow.return_value
    assert sheets._developer_key is None


def test_from_files_cached(oauth2):
    oauth2.file.Storage.return_value.get.return_value.invalid = False

    sheets = gsheets.Sheets.from_files()

    assert isinstance(sheets, gsheets.Sheets)
    assert sheets._creds is oauth2.file.Storage.return_value.get.return_value
    assert sheets._developer_key is None


def test_from_developer_key(mocker):
    sheets = gsheets.Sheets.from_developer_key(mocker.sentinel.developer_key)

    assert isinstance(sheets, gsheets.Sheets)
    assert sheets._creds is None
    assert sheets._developer_key == mocker.sentinel.developer_key


def test_init_fail():
    with pytest.raises(ValueError):
        gsheets.Sheets()


def test_init_developer_key(mocker):
    sheets = gsheets.Sheets(developer_key=mocker.sentinel.developer_key)

    assert isinstance(sheets, gsheets.Sheets)
    assert sheets._creds is None
    assert sheets._developer_key == mocker.sentinel.developer_key


@pytest.mark.usefixtures('files')
def test_len(sheets):
    assert len(sheets) == 1


@pytest.mark.usefixtures('files', 'spreadsheet_values')
def test_iter(sheets):
    assert [s.id for s in sheets] == ['spam']


@pytest.mark.usefixtures('spreadsheet')
def test_contains(sheets):
    assert 'spam' in sheets


@pytest.mark.usefixtures('spreadsheet_404')
def test_contains_fail(sheets):
    assert 'spam' not in sheets


@pytest.mark.usefixtures('spreadsheet_values')
def test_getitem(sheets):
    s = sheets['spam']
    assert s[0][:] == [[1, 2], [3, 4]]


@pytest.mark.usefixtures('spreadsheet_404')
def test_getitem_fail(sheets):
    with pytest.raises(KeyError):
        sheets['spam']


@pytest.mark.usefixtures('files', 'spreadsheet_values')
def test_getitem_all(sheets):
    assert [s.id for s in sheets[:]] == ['spam']


@pytest.mark.usefixtures('spreadsheet_values')
def test_get_id(sheets):
    assert sheets.get('spam').id == 'spam'


@pytest.mark.usefixtures('spreadsheet_values')
def test_get_url(sheets):
    url = 'https://docs.google.com/spreadsheets/d/spam'
    assert sheets.get(url).id == 'spam'


@pytest.mark.usefixtures('spreadsheet_404')
def test_get_fail(sheets):
    assert sheets.get('spam') is None


@pytest.mark.usefixtures('spreadsheet_404')
def test_get_default(sheets):
    default = object()
    assert sheets.get('spam', default) is default


def test_get_invalid(sheets):
    with pytest.raises(ValueError):
        sheets.get('https://spam.com/spam/d/spam')


@pytest.mark.usefixtures('files_name', 'spreadsheet_values')
def test_find(sheets):
    assert sheets.find('Spam').id == 'spam'


@pytest.mark.usefixtures('files_name_unknown')
def test_find_fail(sheets):
    with pytest.raises(KeyError):
        sheets.find('Spam')


@pytest.mark.usefixtures('files_name', 'spreadsheet_values')
def test_findall(sheets):
    assert [s.id for s in sheets.findall('Spam')] == ['spam']


@pytest.mark.usefixtures('files_name_unknown')
def test_findall_fail(sheets, files_name_unknown):
    assert [s.id for s in sheets.findall('Spam')] == []


@pytest.mark.usefixtures('files', 'spreadsheet_values')
def test_findall_all(sheets):
    assert [s.id for s in sheets.findall()] == ['spam']


@pytest.mark.usefixtures('files')
def test_iterfiles(sheets):
    assert list(sheets.iterfiles()) == [('spam', 'Spam')]


@pytest.mark.usefixtures('files')
def test_ids(sheets):
    assert sheets.ids() == ['spam']


@pytest.mark.usefixtures('files')
def test_titles(sheets):
    assert sheets.titles() == ['Spam']


@pytest.mark.usefixtures('files')
def test_titles_unique(sheets):
    assert sheets.titles(unique=True) == ['Spam']
