# coordinates.py - get cell values by sheet coodinates and slices

"""Return cell values and slices from sheet coordinate strings."""

import re
import string

__all__ = ['Coordinates']


def base26int(s, *, _start=1 - ord('A')):
    """Return string ``s`` as ``int`` in bijective base26 notation.

    >>> base26int('SPAM')
    344799
    """
    return sum((_start + ord(c)) * 26**i for i, c in enumerate(reversed(s)))


def base26(x, *, _alphabet=string.ascii_uppercase):
    """Return positive ``int`` ``x`` as string in bijective base26 notation.

    >>> [base26(i) for i in [0, 1, 2, 26, 27, 28, 702, 703, 704]]
    ['', 'A', 'B', 'Z', 'AA', 'AB', 'ZZ', 'AAA', 'AAB']

    >>> base26(344799)  # 19 * 26**3 + 16 * 26**2 + 1 * 26**1 + 13 * 26**0
    'SPAM'

    >>> base26(256)
    'IV'
    """
    result = []
    while x:
        x, digit = divmod(x, 26)
        if not digit:
            x -= 1
            digit = 26
        result.append(_alphabet[digit - 1])
    return ''.join(result[::-1])


class Cells(object):
    """Row-major cell collection for doctests.

        A  B  C
    1 [[1, 2, 3],
    2  [4, 5, 6],
    3  [7, 8, 9]]
    """

    _rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    def __getitem__(self, index):
        coord = Coordinates.from_string(index)
        return coord, coord(self._rows)


class Coordinates(object):
    """Callable fetching values from row major cells.

    >>> Coordinates.from_string('B1')([[1, 2], [3, 4]])
    2

    >>> Cells()[0]
    Traceback (most recent call last):
    ...
    TypeError: expected ...

    >>> Cells()[0:1]
    Traceback (most recent call last):
    ...
    TypeError: expected ...
    """

    _regex = re.compile(r'(?i)'
                        r'\s*(?:'
                        r'(?:(?P<xcol>[A-Z])(?P<xrow>[1-9][0-9]*))'
                        r'|'
                        r'(?P<col>[A-Z])'
                        r'|'
                        r'(?P<row>[1-9][0-9]*)'
                        r')\s*$')

    @staticmethod
    def _parse(coord, *, _match=_regex.match):
        """Return match groups from single sheet coordinate.

        >>> Coordinates._parse('A1')
        ('A', '1', None, None)

        >>> Coordinates._parse('A'), Coordinates._parse('1')
        ((None, None, 'A', None), (None, None, None, '1'))

        >>> Coordinates._parse('spam')
        Traceback (most recent call last):
            ...
        ValueError: spam
        """
        try:
            return _match(coord).groups()
        except AttributeError:
            raise ValueError(coord)

    @staticmethod
    def _cint(col, *, _map={base26(i): i - 1 for i in range(1, 257)}):
        """Return zero-based column index from bijective base26 string.

        >>> Coordinates._cint('Ab')
        27

        >>> Coordinates._cint('spam')
        Traceback (most recent call last):
            ...
        ValueError: spam
        """
        try:
            return _map[col.upper()]
        except KeyError:
            raise ValueError(col)

    @staticmethod
    def _rint(row, *, _int=int):
        return _int(row) - 1

    @classmethod
    def from_string(cls, coord):
        if isinstance(coord, slice):
            return Slice.from_slice(coord)
        xcol, xrow, col, row = cls._parse(coord)
        if xcol is not None:
            return Cell(cls._cint(xcol), cls._rint(xrow))
        elif col is not None:
            return Col(cls._cint(col))
        return Row(cls._rint(row))

    def __repr__(self):
        items = sorted((k, v) for k, v in self.__dict__.items()
                       if not k.startswith('_'))
        args = ', '.join(f'{k}={v!r}' for k, v in items)
        return f'<{self.__class__.__name__}({args})>'


class Cell(Coordinates):
    """

    >>> Cells()['B2']
    (<Cell(col=1, row=1)>, 5)
    """

    def __init__(self, col, row):
        self.col = col
        self.row = row

    def __call__(self, x):
        return x[self.row][self.col]


class Col(Coordinates):
    """

    >>> Cells()['B']
    (<Col(col=1)>, [2, 5, 8])
    """
    def __init__(self, col):
        self.col = col

    def __call__(self, x):
        col = self.col
        return [r[col] for r in x]


class Row(Coordinates):
    """

    >>> Cells()['2']
    (<Row(row=1)>, [4, 5, 6])
    """

    def __init__(self, row):
        self.row = row

    def __call__(self, x):
        return x[self.row][:]


class Slice(Coordinates):
    """

    >>> Cells()[:]
    (<Slice()>, [[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    >>> Cells()['A1':'B3':2]
    Traceback (most recent call last):
    ...
    NotImplementedError: no slice step support
    """

    @classmethod
    def from_slice(cls, coord):
        """Return a value fetching callable given a slice of coordinate strings."""
        if coord.step is not None:
            raise NotImplementedError('no slice step support')
        elif coord.start is not None and coord.stop is not None:
            return DoubleSlice.from_slice(coord)
        elif coord.start is not None:
            xcol, xrow, col, row = cls._parse(coord.start)
            if xcol is not None:
                return StartCell(cls._cint(xcol), cls._rint(xrow))
            elif col is not None:
                return StartCol(cls._cint(col))
            return StartRow(cls._rint(row))
        elif coord.stop is not None:
            xcol, xrow, col, row = cls._parse(coord.stop)
            if xcol is not None:
                return StopCell(cls._cint(xcol) + 1, cls._rint(xrow) + 1)
            elif col is not None:
                return StopCol(cls._cint(col) + 1)
            return StopRow(cls._rint(row) + 1)
        return cls()

    def __call__(self, x):
        return [r[:] for r in x]


class StartCell(Cell, Slice):
    """

    >>> Cells()['B2':]
    (<StartCell(col=1, row=1)>, [[5, 6], [8, 9]])
    """

    def __call__(self, x):
        col = self.col
        return [r[col:] for r in x[self.row:]]


class StopCell(Cell, Slice):
    """

    >>> Cells()[:'B2']
    (<StopCell(col=2, row=2)>, [[1, 2], [4, 5]])
    """

    def __call__(self, x):
        col = self.col
        return [r[:col] for r in x[:self.row]]


class StartCol(Col, Slice):
    """

    >>> Cells()['B':]
    (<StartCol(col=1)>, [[2, 3], [5, 6], [8, 9]])
    """

    def __call__(self, x):
        col = self.col
        return [r[col:] for r in x]


class StopCol(Col, Slice):
    """

    >>> Cells()[:'B']
    (<StopCol(col=2)>, [[1, 2], [4, 5], [7, 8]])
    """

    def __call__(self, x):
        col = self.col
        return [r[:col] for r in x]


class StartRow(Row, Slice):
    """

    >>> Cells()['2':]
    (<StartRow(row=1)>, [[4, 5, 6], [7, 8, 9]])
    """

    def __call__(self, x):
        return x[self.row:]


class StopRow(Row, Slice):
    """

    >>> Cells()[:'2']
    (<StopRow(row=2)>, [[1, 2, 3], [4, 5, 6]])
    """

    def __call__(self, x):
        return x[:self.row]


class DoubleSlice(Slice):

    @classmethod
    def from_slice(cls, coord):
        sxcol, sxrow, scol, srow = cls._parse(coord.start)
        xcol, xrow, col, row = cls._parse(coord.stop)
        if sxcol is not None:
            if xcol is not None:
                sxcol, sxrow = cls._cint(sxcol), cls._rint(sxrow)
                xcol, xrow = cls._cint(xcol), cls._rint(xrow)
                if (sxcol, sxrow) == (xcol, xrow) or sxrow == xrow:
                    return StartCellStopCol(sxcol, sxrow, xcol + 1)
                elif sxcol == xcol:
                    return StartCellStopRow(sxcol, sxrow, xrow + 1)
                elif sxcol > xcol or sxrow > xrow:
                    return Empty()
                return StartCellStopCell(sxcol, sxrow, xcol + 1, xrow + 1)
            elif col is not None:
                sxcol, sxrow, col = cls._cint(sxcol), cls._rint(sxrow), cls._cint(col)
                if sxcol == col:
                    return StartCellStopRow(sxcol, sxrow, None)
                elif sxcol > col:
                    return Empty()
                return StartCellStopCol(sxcol, sxrow, col + 1)
            sxcol, sxrow, row = cls._cint(sxcol), cls._rint(sxrow), cls._rint(row)
            if sxrow == row:
                return StartCellStopCol(sxcol, sxrow, None)
            elif sxrow > row:
                return Empty()
            return StartCellStopRow(sxcol, sxrow, row + 1)
        elif xcol is not None:
            if scol is not None:
                scol, xcol, xrow = cls._cint(scol), cls._cint(xcol), cls._rint(xrow)
                if scol == xcol:
                    return StartRowStopCell(None, xcol, xrow + 1)
                elif scol > xcol:
                    return Empty()
                return StartColStopCell(scol, xcol + 1, xrow)
            srow, xcol, xrow = cls._rint(srow), cls._cint(xcol), cls._rint(xrow)
            if srow == xrow:
                return StartColStopCell(None, xcol + 1, xrow)
            elif srow > xrow:
                return Empty()
            return StartRowStopCell(srow, xcol, xrow + 1)
        elif scol is not None and col is not None:
            scol, col = cls._cint(scol), cls._cint(col)
            if scol == col:
                return Col(scol)
            elif scol > col:
                return Empty()
            return StartColStopCol(scol, col + 1)
        elif srow is not None and row is not None:
            srow, row = cls._rint(srow), cls._rint(row)
            if srow == row:
                return Row(srow)
            elif srow > row:
                return Empty()
            return StartRowStopRow(srow, row + 1)
        elif scol is not None:
            return StartColStopRow(cls._cint(scol), cls._rint(row) + 1)
        return StartRowStopCol(cls._rint(srow), cls._cint(col) + 1)

    def __call__(self, x):
        col = self.col
        return [r[col] for r in x[self.row]]


class Empty(DoubleSlice):

    def __call__(self, x):
        return []


class StartCellStopCell(DoubleSlice):
    """

    >>> Cells()['A1':'B2']
    (<StartCellStopCell(col=slice(0, 2, None), row=slice(0, 2, None))>, [[1, 2], [4, 5]])

    >>> Cells()['A1':'A1']
    (<StartCellStopCol(col=slice(0, 1, None), row=0)>, [1])

    >>> Cells()['A1':'C1']
    (<StartCellStopCol(col=slice(0, 3, None), row=0)>, [1, 2, 3])

    >>> Cells()['A1':'A3']
    (<StartCellStopRow(col=0, row=slice(0, 3, None))>, [1, 4, 7])

    >>> Cells()['B3':'A1']
    (<Empty()>, [])
    """

    def __init__(self, start_col, start_row, stop_col, stop_row):
        self.col = slice(start_col, stop_col)
        self.row = slice(start_row, stop_row)


class StartCellStopCol(Cell, DoubleSlice):
    """

    >>> Cells()['A1':'C']
    (<StartCellStopCol(col=slice(0, 3, None), row=0)>, [1, 2, 3])

    >>> Cells()['A1':'A']
    (<StartCellStopRow(col=0, row=slice(0, None, None))>, [1, 4, 7])

    >>> Cells()['B3':'A']
    (<Empty()>, [])
    """

    def __init__(self, start_col, start_row, stop_col):
        self.col = slice(start_col, stop_col)
        self.row = start_row


class StartCellStopRow(DoubleSlice):
    """

    >>> Cells()['A1':'3']
    (<StartCellStopRow(col=0, row=slice(0, 3, None))>, [1, 4, 7])

    >>> Cells()['A1':'1']
    (<StartCellStopCol(col=slice(0, None, None), row=0)>, [1, 2, 3])

    >>> Cells()['B3':'1']
    (<Empty()>, [])
    """
    def __init__(self, start_col, start_row, stop_row):
        self.col = start_col
        self.row = slice(start_row, stop_row)


class StartColStopCell(Cell, DoubleSlice):
    """

    >>> Cells()['A':'C1']
    (<StartColStopCell(col=slice(0, 3, None), row=0)>, [1, 2, 3])

    >>> Cells()['C':'C3']
    (<StartRowStopCell(col=2, row=slice(None, 3, None))>, [3, 6, 9])

    >>> Cells()['B':'A1']
    (<Empty()>, [])
    """

    def __init__(self, start_col, stop_col, stop_row):
        self.col = slice(start_col, stop_col)
        self.row = stop_row


class StartRowStopCell(DoubleSlice):
    """

    >>> Cells()['1':'A3']
    (<StartRowStopCell(col=0, row=slice(0, 3, None))>, [1, 4, 7])

    >>> Cells()['3':'C3']
    (<StartColStopCell(col=slice(None, 3, None), row=2)>, [7, 8, 9])

    >>> Cells()['3':'A1']
    (<Empty()>, [])
    """
    def __init__(self, start_row, stop_col, stop_row):
        self.col = stop_col
        self.row = slice(start_row, stop_row)


class StartColStopCol(Col, DoubleSlice):
    """

    >>> Cells()['A':'B']
    (<StartColStopCol(col=slice(0, 2, None))>, [[1, 2], [4, 5], [7, 8]])

    >>> Cells()['A':'A']
    (<Col(col=0)>, [1, 4, 7])

    >>> Cells()['B':'A']
    (<Empty()>, [])
    """

    def __init__(self, start_col, stop_col):
        self.col = slice(start_col, stop_col)


class StartRowStopRow(DoubleSlice):
    """

    >>> Cells()['1':'2']
    (<StartRowStopRow(row=slice(0, 2, None))>, [[1, 2, 3], [4, 5, 6]])

    >>> Cells()['1':'1']
    (<Row(row=0)>, [1, 2, 3])

    >>> Cells()['2':'1']
    (<Empty()>, [])
    """

    def __init__(self, start_row, stop_row):
        self.row = slice(start_row, stop_row)

    def __call__(self, x):
        return [r[:] for r in x[self.row]]


class StartColStopRow(DoubleSlice):
    """

    >>> Cells()['A':'3']
    (<StartColStopRow(col=0, row=slice(None, 3, None))>, [1, 4, 7])
    """

    def __init__(self, start_col, stop_row):
        self.col = start_col
        self.row = slice(None, stop_row)


class StartRowStopCol(Cell, DoubleSlice):
    """

    >>> Cells()['1':'C']
    (<StartRowStopCol(col=slice(None, 3, None), row=0)>, [1, 2, 3])
    """

    def __init__(self, start_row, stop_col):
        self.col = slice(None, stop_col)
        self.row = start_row
