# coordinates.py - get cell values by sheet coodinates and slices

"""Return cell values and slices from sheet coordinate strings.

Example:
        A  B  C
    1 [[1, 2, 3],
    2  [4, 5, 6],
    3  [7, 8, 9]]

>>> class Cells(object):
...     def __init__(self, values):
...         self._values = values
...     def __getitem__(self, index):
...         return getter(index)(self._values)
>>> c = Cells([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

>>> c['B2']
5
>>> c['B']
[2, 5, 8]
>>> c['2']
[4, 5, 6]

>>> c['A1':'A1']
[]
>>> c['A1':'C1']
[1, 2]
>>> c['A1':'A3']
[1, 4]
>>> c['A1':'B2']
[[1]]

>>> c['A1':'C']
[1, 2]
>>> c['A1':'3']
[1, 4]
>>> c['1':'A3']
[1, 4]
>>> c['A':'C1']
[1, 2]

>>> c['A':'3']
[1, 4]
>>> c['1':'C']
[1, 2]
>>> c['A':'A']
[]

>>> c['A':'B']
[[1], [4], [7]]
>>> c['1':'2']
[[1, 2, 3]]

>>> c['B2':]
[[5, 6], [8, 9]]
>>> c['B':]
[[2, 3], [5, 6], [8, 9]]
>>> c['2':]
[[4, 5, 6], [7, 8, 9]]

>>> c[:'B2']
[[1]]
>>> c[:'B']
[[1], [4], [7]]
>>> c[:'2']
[[1, 2, 3]]
>>> c[:]
[[1, 2, 3], [4, 5, 6], [7, 8, 9]]

>>> c['B':'A']
[]
>>> c['B1':'A3']
[]
>>> c['A1':'B3':2]
Traceback (most recent call last):
...
NotImplementedError: no slice step support

>>> c[0]
Traceback (most recent call last):
...
TypeError: expected ...
>>> c[0:1]
Traceback (most recent call last):
...
TypeError: expected ...
"""

import re
import string
import itertools

from ._compat import map

__all__ = ['getter']

COORDINATE = r'''(?ix)(?:\s*
    (?P<cell>  (?P<ecol>[A-Z])  (?P<erow>[1-9][0-9]*)  )
|   (?P<col>[A-Z])
|   (?P<row>[1-9][0-9]*)
\s*)$'''

COLUMNS = [string.ascii_lowercase, string.ascii_uppercase]
COLUMNS = map(enumerate, COLUMNS)
COLUMNS = {s: i for i, s in itertools.chain.from_iterable(COLUMNS)}


def getter(index):
    """Return a callable fetching values from row major cells.

    >>> getter('B1')([[1, 2], [3, 4]])
    2
    """
    if isinstance(index, slice):
        return slicegetter(index)
    return itemgetter(index)


def parse(coord, _match=re.compile(COORDINATE).match):
    """Return match group dict from single sheet coordinate.

    >>> sorted(parse('A1').items())
    [('cell', 'A1'), ('col', None), ('ecol', 'A'), ('erow', '1'), ('row', None)]

    >>> parse('spam')
    Traceback (most recent call last):
        ...
    ValueError: spam
    """
    try:
        return _match(coord).groupdict()
    except AttributeError:
        raise ValueError(coord)


def itemgetter(coord, _cint=COLUMNS):
    """Retur a value fetching callable given a single coordinate string."""
    coord = parse(coord)

    if coord['cell'] is not None:
        col = _cint[coord['ecol']]
        row = int(coord['erow']) - 1
        return lambda x: x[row][col]
    elif coord['col'] is not None:
        col = _cint[coord['col']]
        return lambda x: [r[col] for r in x]
    else:
        row = int(coord['row']) - 1
        return lambda x: list(x[row])


def slicegetter(index, _cint=COLUMNS):
    """Retur a value fettching callable given a coordinate string slice."""
    if index.step is not None:
        raise NotImplementedError('no slice step support')

    has_start = index.start is not None
    has_stop = index.stop is not None

    if has_start and has_stop:
        return _slicegetter(parse(index.start), parse(index.stop))
    elif has_start:
        coord = parse(index.start)
        if coord['cell'] is not None:
            col = _cint[coord['ecol']]
            row = int(coord['erow']) - 1
            return lambda x: [r[col:] for r in x[row:]]
        elif coord['col'] is not None:
            col = _cint[coord['col']]
            return lambda x: [r[col:] for r in x]
        else:
            row = int(coord['row']) - 1
            return lambda x: x[row:]
    elif has_stop:
        coord = parse(index.stop)
        if coord['cell'] is not None:
            col = _cint[coord['ecol']]
            row = int(coord['erow']) - 1
            return lambda x: [r[:col] for r in x[:row]]
        elif coord['col'] is not None:
            col = _cint[coord['col']]
            return lambda x: [r[:col] for r in x]
        else:
            row = int(coord['row']) - 1
            return lambda x: x[:row]
    else:
        return lambda x: [r[:] for r in x]


def _slicegetter(start, stop, _cint=COLUMNS):
    """Retur a value fetching callable given slice start and stop."""
    if start == stop:
        return lambda x: []
    elif start['cell'] is not None:
        if stop['cell'] is not None:
            col = slice(_cint[start['ecol']], _cint[stop['ecol']])
            row = slice(int(start['erow']) - 1, int(stop['erow']) - 1)
        elif stop['col'] is not None:
            col = slice(_cint[start['ecol']], _cint[stop['col']])
            row = slice(*2 * (int(start['erow']) - 1,))
        else:
            col = slice(*2 * (_cint[start['ecol']],))
            row = slice(int(start['erow']) - 1, int(stop['row']) - 1)
    elif stop['cell'] is not None:
        if start['col'] is not None:
            col = slice(_cint[start['col']], _cint[stop['ecol']])
            row = slice(*2 * (int(stop['erow']) - 1,))
        else:
            col = slice(*2 * (_cint[stop['ecol']],))
            row = slice(int(start['row']) - 1, int(stop['erow']) - 1)
    elif start['col'] is not None and stop['col'] is not None:
        col = slice(_cint[start['col']], _cint[stop['col']])
        if col.start >= col.stop:
            return lambda x: []
        return lambda x: [r[col] for r in x]
    elif start['row'] is not None and stop['row'] is not None:
        row = slice(int(start['row']) - 1, int(stop['row']) - 1)
        return lambda x: x[row]
    elif start['col'] is not None:
        col = _cint[start['col']]
        row = int(stop['row']) - 1
        return lambda x: [r[col] for r in x[:row]]
    elif start['row'] is not None:
        row = int(start['row']) - 1
        col = _cint[stop['col']]
        return lambda x: x[row][:col]
    else:  # pragma: no cover
        raise NotImplementedError

    if row.start == row.stop:
        return lambda x: x[row.start][col]
    elif col.start == col.stop:
        col = col.start
    elif col.start > col.stop:
        return lambda x: []
    return lambda x: [r[col] for r in x[row]]
