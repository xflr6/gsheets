# test_api.py

import pytest

import gsheets


@pytest.fixture
def sheets():
    return gsheets.Sheets(credentials=None)


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


def test_from_files_cached(oauth2):
    oauth2.file.Storage.return_value.get.return_value.invalid = False

    sheets = gsheets.Sheets.from_files()

    assert isinstance(sheets, gsheets.Sheets)
    assert sheets._creds is oauth2.file.Storage.return_value.get.return_value


def test_len(sheets, files_all):
    assert len(sheets) == 1


def test_iter(sheets, files_all, spreadsheet_values):
    assert [s.id for s in sheets] == ['spam']


def test_contains(sheets, spreadsheet):
    assert 'spam' in sheets


def test_contains_fail(sheets, spreadsheet_404):
    assert 'spam' not in sheets


def test_getitem(sheets, spreadsheet_values):
    s = sheets['spam']
    assert s[0][:] == [[1, 2], [3, 4]]


def test_getitem_fail(sheets, spreadsheet_404):
    with pytest.raises(KeyError):
        sheets['spam']


def test_getitem_all(sheets, files_all, spreadsheet_values):
    assert [s.id for s in sheets[:]] == ['spam']


def test_get_id(sheets, spreadsheet_values):
    assert sheets.get('spam').id == 'spam'


def test_get_url(sheets, spreadsheet_values):
    url = 'https://docs.google.com/spreadsheets/d/spam'
    assert sheets.get(url).id == 'spam'


def test_get_fail(sheets, spreadsheet_404):
    assert sheets.get('spam') is None


def test_get_default(sheets, spreadsheet_404):
    default = object()
    assert sheets.get('spam', default) is default


def test_get_invalid(sheets):
    with pytest.raises(ValueError):
        sheets.get('https://spam.com/spam/d/spam')


def test_find(sheets, files_name, spreadsheet_values):
    assert sheets.find('Spam').id == 'spam'


def test_find_fail(sheets, files_name_unknown):
    with pytest.raises(KeyError):
        sheets.find('Spam')


def test_findall(sheets, files_name, spreadsheet_values):
    assert [s.id for s in sheets.findall('Spam')] == ['spam']


def test_findall_fail(sheets, files_name_unknown):
    assert [s.id for s in sheets.findall('Spam')] == []


def test_findall_all(sheets, files_all, spreadsheet_values):
    assert [s.id for s in sheets.findall()] == ['spam']


def test_iterfiles(sheets, files_all):
    assert list(sheets.iterfiles()) == [('spam', 'Spam')]


def test_ids(sheets, files_all):
    assert sheets.ids() == ['spam']


def test_titles(sheets, files_all):
    assert sheets.titles() == ['Spam']


def test_titles_unique(sheets, files_all):
    assert sheets.titles(unique=True) == ['Spam']
