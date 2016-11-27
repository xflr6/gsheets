.. _api:

API Reference
=============


Sheets
------

.. autoclass:: gsheets.Sheets
    :members:
        from_files,
        __len__, __iter__, __contains__, __getitem__, get,
        find, findall,
        iterfiles, ids, titles

SpreadSheet
-----------

.. autoclass:: gsheets.models.SpreadSheet
    :members:
        __len__, __iter__, __contains__, __getitem__, get,
        find, findall, sheets,
        id, title, url, first_sheet,
        to_csv


SheetsView
----------

.. autoclass:: gsheets.models.SheetsView
    :members:
        __getitem__,
        ids, titles


WorkSheet
---------

.. autoclass:: gsheets.models.WorkSheet
    :members:
        __getitem__, at, values,
        spreadsheet,
        id, title, url, index ,nrows, ncols, ncells,
        to_csv, to_frame
