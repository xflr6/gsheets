# test_models.py

import sys

import mock
import pytest

import gsheets

PY2 = sys.version_info[0] == 2


@pytest.fixture
def sheet(spreadsheet_values):
    id = spreadsheet_values['spreadsheet']['spreadsheetId']
    yield gsheets.Sheets(credentials=None)[id]


@pytest.fixture
def view(sheet):
    yield sheet.sheets


@pytest.fixture
def ws(sheet):
    yield sheet[0]


@pytest.fixture
def ws_nonascii(ws):
    ws._values = [[u'Sp\xe4m', u'Eggs'], [None, 1]]
    yield ws


class TestSpreadSheet(object):

    def test_repr(self, sheet):
        assert repr(sheet) == "<SpreadSheet spam 'Spam'>"

    def test_eq(self, sheet):
        assert sheet == sheet

    def test_eq_fail(self, sheet):
        assert not sheet == object()

    def test_ne(self, sheet):
        assert sheet != object()

    def test_ne_fail(self, sheet):
        assert not sheet != sheet

    def test_len(self, sheet):
        assert len(sheet) == 1

    def test_iter(self, sheet):
        assert [s.id for s in sheet] == [0]

    def test_contains(self, sheet):
        assert 0 in sheet and -1 not in sheet

    def test_contains_invalid(self, sheet):
        with pytest.raises(TypeError):
            'spam' in sheet

    def test_getitem(self, sheet):
        assert sheet[0].id == 0

    def test_getitem_fail(self, sheet):
        with pytest.raises(KeyError):
            sheet[-1]

    def test_getitem_invalid(self, sheet):
        with pytest.raises(TypeError):
            sheet['spam']

    def test_get(self, sheet):
        assert sheet.get(0).id == 0

    def test_get_fail(self, sheet):
        assert sheet.get(-1) is None

    def test_get_default(self, sheet):
        assert sheet.get(-1, mock.sentinel.default) is mock.sentinel.default

    def test_get_invalid(self, sheet):
        with pytest.raises(TypeError):
            sheet.get('spam')

    def test_find(self, sheet):
        assert sheet.find('Spam1').title == 'Spam1'

    def test_find_fail(self, sheet):
        with pytest.raises(KeyError):
            sheet.find('Eggs1')

    def test_findall(self, sheet):
        assert sheet.findall('Spam1') == [sheet[0]]

    def test_findall_fail(self, sheet):
        assert sheet.findall('Eggs1') == []

    def test_findall_all(self, sheet):
        assert sheet.findall(None) == [sheet[0]]

    def test_sheets(self, sheet):
        assert isinstance(sheet.sheets, gsheets.models.SheetsView)

    def test_id(self, sheet):
        assert sheet.id == 'spam'

    def test_title(self, sheet):
        assert sheet.title == 'Spam'

    def test_url(self, sheet):
        assert sheet.url == 'https://docs.google.com/spreadsheets/d/spam/edit#gid=0'

    def test_first_sheet(self, sheet):
        assert sheet.first_sheet is sheet.sheets[0]

    def test_to_csv(self, sheet):
        TestWorkSheet._to_csv(sheet)


class TestSheetsView(object):

    def test_eq_fail(self, view):
        assert not view == list(view)

    def test_ne_fail(self, view):
        assert view != list(view)

    def test_getitem(self, view):
        assert view[0].id == 0

    def test_getitem_fail(self, view):
        with pytest.raises(IndexError):
            view[23]

    def test_ids(self, view):
        assert view.ids() == [0]

    def test_titles(self, view):
        assert view.titles() == ['Spam1']

    def test_titles_unique(self, view):
        assert view.titles(unique=True) == ['Spam1']


class TestWorkSheet(object):

    def test_repr(self, ws):
        assert repr(ws) == "<WorkSheet 0 'Spam1' (2x2)>"

    def test_eq_fail(self, ws):
        assert not ws == ws.values()

    def test_ne_fail(self, ws):
        assert ws != ws.values()

    def test_getitem(self, ws):
        assert ws[:] == [[1, 2], [3, 4]]

    def test_getitem_fail(self, ws):
        with pytest.raises(IndexError):
            ws['Z23']

    def test_getitem_invalid(self, ws):
        with pytest.raises(ValueError):
            ws['spam']

    def test_getitem_int(self, ws):
        with pytest.raises(TypeError):
            ws[0]

    def test_at(self, ws):
        assert ws.at(0, 0) == 1 and ws.at(1, 1) == 4

    def test_at_fail(self, ws):
        with pytest.raises(TypeError):
            ws.at('A', '1')

    def test_at_invalid(self, ws):
        with pytest.raises(IndexError):
            ws.at(23, 23)

    def test_values(self, ws):
        assert ws.values() == [[1, 2], [3, 4]]

    def test_values_column_major(self, ws):
        assert ws.values(True) == [[1, 3], [2, 4]]

    def test_spreadseet(self, ws):
        assert ws.spreadsheet.id == 'spam'

    def test_id(self, ws):
        assert ws.id == 0

    def test_title(self, ws):
        assert ws.title == 'Spam1'

    def test_url(self, ws):
        assert ws.url == 'https://docs.google.com/spreadsheets/d/spam/edit#gid=0'

    def test_index(self, ws):
        assert ws.index == 0

    def test_ncells(self, ws):
        assert ws.ncells == 4

    def test_to_csv(self, ws):
        self._to_csv(ws)

    def test_to_csv_func(self, ws):
        make_filename = lambda infos: '%(title)s-%(index)s-%(sheet)s.csv' % infos
        self._to_csv(ws, make_filename=make_filename, filename='Spam-0-Spam1.csv')

    def test_to_csv_nonascii(self, ws_nonascii):
        if PY2:
            self._to_csv(ws_nonascii, lines=['Sp\xc3\xa4m,Eggs\r\n', ',1\r\n'])
        else:
            self._to_csv(ws_nonascii, lines=[u'Sp\xe4m,Eggs\r\n', u',1\r\n'])

    @staticmethod
    def _to_csv(obj, make_filename=None, lines=['1,2\r\n', '3,4\r\n'],
                filename='Spam - Spam1.csv', encoding='utf-8'):
        with mock.patch('gsheets._compat.open', mock.mock_open()) as open_:
            obj.to_csv(make_filename=make_filename)

        if PY2:
            open_.assert_called_once_with(filename, 'wb')
        else:
            open_.assert_called_once_with(filename, 'w', encoding=encoding, newline='')
        assert open_.return_value.write.call_args_list == [mock.call(l,) for l in lines]

    def test_to_frame(self, ws):
        self._to_frame(ws)

    def test_to_frame_nonascii(self, ws_nonascii):
        if PY2:
            self._to_frame(ws_nonascii, 'Sp\xc3\xa4m,Eggs\r\n,1\r\n')
        else:
            self._to_frame(ws_nonascii, u'Sp\xe4m,Eggs\r\n,1\r\n')

    @staticmethod
    def _to_frame(ws, data='1,2\r\n3,4\r\n', name='Spam1'):
        def read_csv(fd, encoding, dialect):
            if PY2:
                assert encoding == 'utf-8' and dialect == 'excel'
            else:
                assert encoding is None and dialect == 'excel'
            assert fd.getvalue() == data
            return mock.NonCallableMock()
        with mock.patch('gsheets.export.pandas') as pandas:
            pandas.read_csv.side_effect = read_csv
            df = ws.to_frame()
        assert df.name == name
