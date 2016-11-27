# _compat.py - Python 2/3 compatibility

import sys

PY2 = sys.version_info[0] == 2

if PY2:  # pragma: no cover
    text_type = unicode
    string_types = basestring

    def iteritems(d):
        return d.iteritems()

    from itertools import imap as map, izip as zip

    def open_csv(name, mode=None, encoding=None):
        if mode is None:
            mode = ''
        if 'b' not in mode:
            mode += 'b'
        return open(name, mode)

    def csv_writerows(csvfile, rows, encoding):
        for r in rows:
            data = [(u'%s' % c).encode(encoding) if c is not None else c for c in r]
            csvfile.writerow(data)

    try:
        from cStringIO import StringIO as CsvBuffer
    except ImportError:
        from StringIO import StringIO as CsvBuffer

    def read_csv(pandas, fd, encoding, dialect, kwargs):
        return pandas.read_csv(fd, encoding=encoding, dialect=dialect, **kwargs)


else:  # pragma: no cover
    text_type = string_types = str

    def iteritems(d):
        return iter(d.items())

    map, zip = map, zip

    def open_csv(name, mode=None, encoding=None):
        return open(name, mode, encoding=encoding, newline='')

    def csv_writerows(csvfile, rows, encoding):
        csvfile.writerows(rows)

    from io import StringIO as CsvBuffer

    def read_csv(pandas, fd, encoding, dialect, kwargs):
        return pandas.read_csv(fd, encoding=None, dialect=dialect, **kwargs)
