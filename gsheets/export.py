# export.py - write csv, read csv buffer into pandas dataframe

"""Dump spreadsheet values to CSV files and pandas DataFrames."""

import csv
import io

pandas = None

__all__ = ['ENCODING', 'write_csv', 'write_dataframe']

ENCODING = 'utf-8'

DIALECT = 'excel'

MAKE_FILENAME = '%(title)s - %(sheet)s.csv'


def write_csv(fileobj, rows, *, dialect=DIALECT):
    """Dump rows to ``fileobj`` with the given CSV ``dialect``."""
    csvwriter = csv.writer(fileobj, dialect=dialect)
    csvwriter.writerows(rows)


def write_dataframe(rows, *, dialect=DIALECT, **kwargs):
    """Dump ``rows`` to string buffer and load with ``pandas.read_csv()`` using ``kwargs``."""
    global pandas
    if pandas is None:  # pragma: no cover
        import pandas

    with io.StringIO() as fd:
        write_csv(fd, rows, dialect=dialect)
        fd.seek(0)
        df = pandas.read_csv(fd, dialect=dialect, **kwargs)

    return df
