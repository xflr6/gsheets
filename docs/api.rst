.. _api:

API Reference
=============


.. autosummary::
    :nosignatures:

    gsheets.Sheets
    gsheets.models.SpreadSheet
    gsheets.models.SheetsView
    gsheets.models.WorkSheet
    gsheets.get_credentials
    gsheets.build_service


Sheets
------

.. autoclass:: gsheets.Sheets
    :members:
        from_files, from_developer_key,
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


Low-level functions
-------------------

.. autofunction:: gsheets.get_credentials
.. autofunction:: gsheets.build_service
