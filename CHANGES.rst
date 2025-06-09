Changelog
=========


Version 0.6.2 (in development)
------------------------------

Switch to pyproject.toml.

Drop Python 3.7 support and tag Python 3.11 support.


Version 0.6.1
-------------

Drop Python 3.6 support.


Version 0.6
-----------

Drop Python 2 support.

Fix loading of sheets that contain worksheets with titles that are also a valid
reference in A1-notation (add quoting, GH #21).

Drop Python 3.5 support and tag Python 3.9 and 3.10 support.

Changed a few optional flags to keyword-only arguments.

Migrate CI to GitHub actions and extend build matrix.


Version 0.5.1
-------------

Avoid ``file_cache`` import warning with oauth2client >= 4.


Version 0.5
-----------

Add support for API key auth: add optional ``developer_key`` argument to
``Sheets`` constructor and alternate ``Sheets.from_developer_key()``
constructor, see also
https://developers.google.com/sheets/api/guides/authorizing (PR Natarajan
Krishnaswami).

Improve test and doc building config.


Version 0.4.1
-------------

Fix documentation example of ``make_filename``.

Tag Python 3.7 and 3.8 support.


Version 0.4
-----------

Change ``ws.to_frame()`` method to make assignment of worksheet title to ``name``
attribute of ``pandas.DataFrame`` opt-in by ``assign_name`` kwarg.


Version 0.3.2
-------------

Drop Python 3.4 support.


Version 0.3.1
-------------

Add/fix oauth2client dependency (dropped from google-api-python-client).

Drop Python 3.3 support, tag Python 3.7 support.


Version 0.3
-----------

Fetch datetime values as strings instead of days since December 30th 1899
(backwards imcompatible, PR Andrea Nardelli).

Fix handling of empty worksheets (PR lanfon72).

Include LICENSE file in wheel.


Version 0.2
-----------

Make A1 notation slices inclusive (backwards incompatible).

Also support template strings for ``make_filename``.

Change ``make_filename`` callable to a one argument functon given a dictionary.

Add equivalence for ``SpreadSheet``, ``SheetsView``, and ``WorkSheet``.

Include ``get_credentials()`` and ``build_service()`` as low-level api functions.

Add ``no_webserver`` auth for working on remote machines.

Change default filename for client secrets to ``'client_secrets.json'``.

Include docs in source distribution.


Version 0.1
-----------

First release (read-only access).
