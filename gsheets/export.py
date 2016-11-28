# export.py - write csv, read csv buffer into pandas dataframe

"""Dump spreadsheet values to CSV files and pandas DataFrames."""

import csv
import contextlib

from ._compat import open_csv, csv_writerows, CsvBuffer, read_csv

pandas = None

__all__ = ['open_csv', 'write_csv', 'write_dataframe']

ENCODING = 'utf-8'

DIALECT = 'excel'

MAKE_FILENAME = '%(title)s - %(sheet)s.csv'


def write_csv(fileobj, rows, encoding=ENCODING, dialect=DIALECT):
    """Dump rows to fileobj with the given encoding and CSV dialect."""
    csvfile = csv.writer(fileobj, dialect=dialect)
    csv_writerows(csvfile, rows, encoding)


def write_dataframe(rows, encoding=ENCODING, dialect=DIALECT, **kwargs):
    """Dump rows to string buffer and load with pandas.read_csv using kwargs."""
    global pandas
    if pandas is None:  # pragma: no cover
        import pandas
    with contextlib.closing(CsvBuffer()) as fd:
        write_csv(fd, rows, encoding, dialect)
        fd.seek(0)
        df = read_csv(pandas, fd, encoding, dialect, kwargs)
    return df
