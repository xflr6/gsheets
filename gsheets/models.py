# models.py - library user facing objects

"""Python objects for spreadsheets consisting of worksheets."""

from . import backend
from . import coordinates
from . import export
from . import tools
from . import urls

__all__ = ['SpreadSheet', 'SheetsView', 'WorkSheet']


class SpreadSheet(object):
    """Fetched collection of worksheets."""

    @classmethod
    def _from_response(cls, response, service):
        id = response['spreadsheetId']
        title = response['properties']['title']
        ranges = [s['properties']['title'] for s in response['sheets']]
        values = backend.values(service, id, ranges)
        sheets = map(WorkSheet._from_response, response['sheets'], values)
        return cls(id, title, list(sheets), service)

    def __init__(self, id, title, sheets, service):
        self._id = id
        self._title = title
        self._url = urls.SheetUrl(self._id)
        self._sheets = sheets
        for s in sheets:
            s._spreadsheet = self
        self._map = {s.id: s for s in sheets}
        self._titles = tools.group_dict(sheets, lambda s: s.title)
        self._service = service

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._url.short_id} {self._title!r}>'

    def __eq__(self, other):
        if isinstance(other, SpreadSheet):
            return self.sheets == other.sheets
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, SpreadSheet):
            return self.sheets != other.sheets
        return NotImplemented

    def __len__(self):
        """Return the number of contained worksheets.

        Returns:
            int: number of worksheets
        """
        return len(self._sheets)

    def __iter__(self):
        """Yield all contained worksheets.

        Yields:
            WorkSheet objects (spreadsheet members)
        """
        return iter(self._sheets)

    def __contains__(self, id):
        """Return if the spreadsheet has a worksheet with the given id.

        Args:
            id (int): numeric id of the worksheet
        Returns:
            bool: ``True`` if such a worksheet is present else ``False``
        Raises:
            TypeError: if ``id`` is not an ``int``
        """
        if not isinstance(id, int):
            raise TypeError(id)
        return id in self._map

    def __getitem__(self, id):
        """Return the worksheet with the given id.

        Args:
            id: numeric id of the worksheet
        Returns:
            WorkSheet: contained worksheet object
        Raises:
            TypeError: if ``id`` is not an ``int``
            KeyError: if the spreadsheet has no worksheet with the given ``id``
        """
        if not isinstance(id, int):
            raise TypeError(id)
        return self._map[id]

    def get(self, id, default=None):
        """Return the worksheet with the given id or the given default.

        Args:
            id: numeric id of the worksheet
        Returns:
            WorkSheet: contained worksheet object or given default
        Raises:
            ValueError: if ``id`` is not an ``int``
        """
        try:
            return self[id]
        except KeyError:
            return default

    def find(self, title):
        """Return the first worksheet with the given title.

        Args:
            title(str): title/name of the worksheet to return
        Returns:
            WorkSheet: contained worksheet object
        Raises:
            KeyError: if the spreadsheet has no no worksheet with the given ``title``
        """
        if title not in self._titles:
            raise KeyError(title)
        return self._titles[title][0]

    def findall(self, title=None):
        """Return a list of worksheets with the given title.

        Args:
            title(str): title/name of the worksheets to return, or ``None`` for all
        Returns:
            list: list of contained worksheet instances (possibly empty)
        """
        if title is None:
            return list(self._sheets)
        if title not in self._titles:
            return []
        return list(self._titles[title])

    def values(self, a1_notation):
        """

        see https://developers.google.com/sheets/guides/concepts#a1_notation
        """

    @property
    def sheets(self):
        """List view of the worksheets in the spreadsheet (positional access). """
        return SheetsView(self._sheets)

    @property
    def id(self):
        """Unique alphanumeric id of the spreadsheet (``str``).

        see https://developers.google.com/sheets/guides/concepts#spreadsheet_id
        """
        return self._id

    @property
    def title(self):
        """Title/name of the spreadsheet (``str``)."""
        return self._title

    @property
    def url(self):
        """URL pointing to the first worksheet of the spreadsheet (``str``)."""
        return self._url.to_string()

    @property
    def first_sheet(self):
        """The first worksheet of the spreadsheet."""
        return self._sheets[0]

    def to_csv(self, *,
               encoding=export.ENCODING,
               dialect=export.DIALECT,
               make_filename=export.MAKE_FILENAME):
        """Dump all worksheets of the spreadsheet to individual CSV files.

        Args:
            encoding (str): result string encoding
            dialect (str): :mod:`csv` dialect name or object to use
            make_filename: template or one-argument callable returning the filename

        If ``make_filename`` is a string, it is string-interpolated with an
        infos-dictionary with the fields ``id`` (spreadhseet id), ``title``
        (spreadsheet title), ``sheet`` (worksheet title), ``gid`` (worksheet
        id), ``index`` (worksheet index), and ``dialect`` CSV dialect to
        generate the filename: ``filename = make_filename % infos``.

        If ``make_filename`` is a callable, it will be called with the
        infos-dictionary to generate the filename:
        ``filename = make_filename(infos)``.
        """
        for s in self._sheets:
            s.to_csv(None,
                     encoding=encoding,
                     dialect=dialect,
                     make_filename=make_filename)


class SheetsView(tools.list_view):
    """Read-only view on the list of worksheets in a spreadsheet."""

    def __eq__(self, other):
        if isinstance(other, SheetsView):
            return (self.titles() == other.titles()
                    and all(s == o for s, o in zip(self._items, other._items)))
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, SheetsView):
            return (self.titles() != other.titles()
                    or any(s != o for s, o in zip(self._items, other._items)))
        return NotImplemented

    def __getitem__(self, index):
        """Return the worksheet at the given index (position).

        Args:
            index: zero-based position or slice
        Raises:
            IndexError: if ``index`` is out of range
        """
        return self._items[index]

    def ids(self):
        """Return a list of contained worksheet ids.

        Returns:
            list: list of numeric ids (``int``)
        """
        return [s.id for s in self._items]

    def titles(self, *, unique=False):
        """Return a list of contained worksheet titles.

        Args:
            unique (bool): drop duplicates
        Returns:
            list: list of titles/name strings
        """
        if unique:
            return tools.uniqued(s.title for s in self._items)
        return [s.title for s in self._items]


class WorkSheet(object):
    """Two-dimensional table with cells accessible via A1 notation."""

    @classmethod
    def _from_response(cls, response, valuerange):
        prop = response['properties']
        id = prop['sheetId']
        title = prop['title']
        index = prop['index']
        values = valuerange.get('values', [[]])
        return cls(id, title, index, values)

    def __init__(self, id, title, index, values):
        self._id = id
        self._title = title
        self._index = index
        self._values = values
        self._spreadsheet = None

    def __repr__(self):
        return (f'<{self.__class__.__name__} {self._id:d} {self._title!r}'
                f' ({self.nrows:d}x{self.ncols:d})>')

    def __eq__(self, other):
        if isinstance(other, WorkSheet):
            return self._values == other._values
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, WorkSheet):
            return self._values != other._values
        return NotImplemented

    def __getitem__(self, index):
        """Return the value(s) of the given cell(s).

        Args:
            index (str): cell/row/col index ('A1', '2', 'B') or slice ('A1':'C3')
        Returns:
            value (cell), list(col, row), or nested list (two-dimentional slice)
        Raises:
            TypeError: if ``index`` is not a string or slice of strings
            ValueError: if ``index`` canot be parsed
            IndexError: if ``index`` is out of range
        """
        getter = coordinates.Coordinates.from_string(index)
        return getter(self._values)

    def at(self, row, col):
        """Return the value at the given cell position.

        Args:
           row (int): zero-based row number
           col (int): zero-based column number
        Returns:
            cell value
        Raises:
            TypeError: if ``row`` or ``col`` is not an ``int``
            IndexError: if the position is out of range
        """
        if not (isinstance(row, int) and isinstance(col, int)):
            raise TypeError(row, col)
        return self._values[row][col]

    def values(self, *, column_major=False):
        """Return a nested list with the worksheet values.

        Args:
            column_major (bool): as list of columns (default list of rows)
        Returns:
            list: list of lists with values
        """
        if column_major:
            return list(map(list, zip(*self._values)))
        return [row[:] for row in self._values]

    @property
    def spreadsheet(self):
        """Containing spreadsheet of the worksheet."""
        return self._spreadsheet

    @property
    def id(self):
        """Stable numeric worksheet id (``int``), unique within its spreadsheet.

        see https://developers.google.com/sheets/guides/concepts#sheet_id
        """
        return self._id

    @property
    def title(self):
        """Worksheet title/name (``str``)."""
        return self._title

    @property
    def url(self):
        """URL pointing to the worksheet (``str``)."""
        return self._spreadsheet._url.to_string(gid=self.id)

    @property
    def index(self):
        """Zero-based position of the worksheet."""
        return self._index

    @property
    def nrows(self):
        """Number of rows in the worksheet (``int``)."""
        return len(self._values)

    @property
    def ncols(self):
        """Number of columns in the worksheet (int)."""
        return len(self._values[0])

    @property
    def ncells(self):
        """Number of cells in the worksheet (``int``)."""
        return self.nrows * self.ncols

    def to_csv(self, filename=None, *,
               encoding=export.ENCODING,
               dialect=export.DIALECT,
               make_filename=export.MAKE_FILENAME):
        """Dump the worksheet to a CSV file.

        Args:
            filename (str): result filename (if ``None`` use ``make_filename``)
            encoding (str): result string encoding
            dialect (str): :mod:`csv` dialect name or object to use
            make_filename: template or one-argument callable returning the filename

        If ``make_filename`` is a string, it is string-interpolated with an
        infos-dictionary with the fields ``id`` (spreadhseet id), ``title``
        (spreadsheet title), ``sheet`` (worksheet title), ``gid`` (worksheet
        id), ``index`` (worksheet index), and ``dialect`` CSV dialect to
        generate the filename: ``filename = make_filename % infos``.

        If ``make_filename`` is a callable, it will be called with the
        infos-dictionary to generate the filename:
        ``filename = make_filename(infos)``.
        """
        if filename is None:
            if make_filename is None:
                make_filename = export.MAKE_FILENAME
            infos = {'id': self._spreadsheet._id,
                    'title': self._spreadsheet._title,
                    'sheet': self._title,
                    'gid': self._id,
                    'index': self._index,
                    'dialect': dialect}
            if isinstance(make_filename, str):
                filename = make_filename % infos
            else:
                filename = make_filename(infos)
        with open(filename, 'w', encoding=encoding, newline='') as fd:
            export.write_csv(fd, self._values, dialect=dialect)

    def to_frame(self, *, assign_name=False, **kwargs):
        r"""Return a pandas DataFrame loaded from the worksheet data.

        Args:
            assign_name (bool): set name attribute on the DataFrame to sheet title.
            \**kwargs: passed to ``pandas.read_csv()`` (e.g. ``header``, ``index_col``)
        Returns:
            pandas.DataFrame: new ``DataFrame`` instance
        """
        df = export.write_dataframe(self._values, **kwargs)
        if assign_name:
            df.name = self.title
        return df
