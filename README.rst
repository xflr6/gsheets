gsheets
=======

|PyPI version| |License| |Supported Python| |Format|

|Build| |Codecov| |Readthedocs-stable| |Readthedocs-latest|

``gsheets`` is a small wrapper around the `Google Sheets API`_ (v4) to provide
more convenient access to `Google Sheets`_ from Python scripts.

`Turn on the API`_, download an OAuth client ID as JSON file, and create a
``Sheets`` object from it. Use its index access (``__getitem__``) to retrieve
SpreadSheet objects by their id, or use ``.get()`` with a sheet URL.
Iterate over the ``Sheets`` object for all spreadsheets, or fetch spreadsheets
by title with the ``.find()`` and ``.findall()`` methods.

SpreadSheet objects are collections of WorkSheets, which provide access to the
cell values via spreadsheet coordinates/slices (e.g. ``ws['A1']``) and
zero-based cell position (e.g. ``ws.at(0, 1)``).

Save WorkSheets (or all from a SpreadSheet) as CSV files with the
``.to_csv()``-method. Create ``pandas.DataFrames`` from worksheet with the
``.to_frame()``-method.


Links
-----

- GitHub: https://github.com/xflr6/gsheets
- PyPI: https://pypi.org/project/gsheets/
- Documentation: https://gsheets.readthedocs.io
- Changelog: https://gsheets.readthedocs.io/en/latest/changelog.html
- Issue Tracker: https://github.com/xflr6/gsheets/issues
- Download: https://pypi.org/project/gsheets/#files


Installation
------------

This package runs under Python 3.6+, use pip_ to install:

.. code:: bash

    $ pip install gsheets

This will also install google-api-python-client_ and its dependencies, notably
httplib2_ and oauth2client_, as required dependencies.


Quickstart
----------

Log into the `Google Developers Console`_ with the Google account whose
spreadsheets you want to access. Create (or select) a project and enable the
**Drive API** and **Sheets API** (under **Google Apps APIs**).

Go to the **Credentials** for your project and create **New credentials** >
**OAuth client ID** > of type **Other**. In the list of your **OAuth 2.0 client
IDs** click **Download JSON** for the Client ID you just created. Save the
file as ``client_secrets.json`` in your home directory (user directory).
Another file, named ``storage.json`` in this example, will be created after
successful authorization to cache OAuth data.

On you first usage of ``gsheets`` with this file (holding the client secrets),
your webbrowser will be opened, asking you to log in with your Google account
to authorize this client read access to all its Google Drive files and Google
Sheets.

Create a sheets object:

.. code:: python

    >>> from gsheets import Sheets

    >>> sheets = Sheets.from_files('~/client_secrets.json', '~/storage.json')
    >>> sheets  #doctest: +ELLIPSIS
    <gsheets.api.Sheets object at 0x...>

Fetch a spreadsheet by id or url:

.. code:: python

    # id only
    >>> sheets['1dR13B3Wi_KJGUJQ0BZa2frLAVxhZnbz0hpwCcWSvb20']
    <SpreadSheet 1dR13...20 'Spam'>

    # id or url
    >>> url = 'https://docs.google.com/spreadsheets/d/1dR13B3Wi_KJGUJQ0BZa2frLAVxhZnbz0hpwCcWSvb20'
    >>> s = sheets.get(url)  
    >>> s
    <SpreadSheet 1dR13...20 'Spam'>

Access worksheets and their values:

.. code:: python

    # first worksheet with title
    >>> s.find('Tabellenblatt2')
    <WorkSheet 1747240182 'Tabellenblatt2' (10x2)>

    # worksheet by position, cell value by index
    >>> s.sheets[0]['A1']
    'spam'

    # worksheet by id, cell value by position
    >>> s[1747240182].at(row=1, col=1)
    1

Dump a worksheet to a CSV file:

.. code:: python

    >>> s.sheets[1].to_csv('Spam.csv', encoding='utf-8', dialect='excel')

Dump all worksheet to a CSV file (deriving filenames from spreadsheet and
worksheet title):

.. code:: python

    >>> csv_name = lambda infos: '%(title)s - %(sheet)s.csv' % infos
    >>> s.to_csv(make_filename=csv_name)

Load the worksheet data into a pandas DataFrame (requires ``pandas``):

.. code:: python

    >>> s.find('Tabellenblatt2').to_frame(index_col='spam')
          eggs
    spam      
    spam  eggs
    ...

``WorkSheet.to_frame()`` passes its kwargs on to ``pandas.read_csv()`` 


See also
--------

- gsheets.py_ |--| self-containd script to dump all worksheets of a Google
  Spreadsheet to CSV or convert any subsheet to a pandas DataFrame (Python 2
  prototype for this library)
- gspread_ |--| Google Spreadsheets Python API (more mature and featureful
  Python wrapper, currently using the XML-based `legacy v3 API`_)
- `example Jupyter notebook`_ using gspread_ to fetch a sheet into a pandas
  DataFrame
- df2gspread_ |--| Transfer data between Google Spreadsheets and Pandas (build
  upon gspread_, currently Python 2 only, GPL)
- pygsheets_ |--| Google Spreadsheets Python API v4 (v4 port of gspread_
  providing further extensions)
- gspread-pandas_ |--| Interact with Google Spreadsheet through Pandas DataFrames
- pgsheets_ |--| Manipulate Google Sheets Using Pandas DataFrames (independent
  bidirectional transfer library, using the `legacy v3 API`_, Python 3 only)
- PyDrive_ |--| Google Drive API made easy (google-api-python-client_ wrapper
  for the `Google Drive`_ API, currently v2) 


License
-------

This package is distributed under the `MIT license`_.


.. _Google Sheets API: https://developers.google.com/sheets/
.. _Google Sheets: https://sheets.google.com
.. _Google Drive: https://drive.google.com
.. _Turn on the API: https://developers.google.com/sheets/quickstart/python#step_1_turn_on_the_api_name

.. _pip: https://pip.readthedocs.io
.. _google-api-python-client: https://pypi.org/project/google-api-python-client/
.. _httplib2: https://pypi.org/project/httplib2/
.. _oauth2client: https://pypi.org/project/oauth2client/
.. _rsa: https://pypi.org/project/rsa/

.. _Google Developers Console: https://console.developers.google.com

.. _gsheets.py: https://gist.github.com/xflr6/57508d28adec1cd3cd047032e8d81266
.. _gspread: https://pypi.org/project/gspread/
.. _legacy v3 API: https://developers.google.com/google-apps/spreadsheets/
.. _example Jupyter notebook: https://gist.github.com/egradman/3b8140930aef97f9b0e4
.. _df2gspread: https://pypi.org/project/df2gspread/
.. _pygsheets : https://pypi.org/project/pygsheets/
.. _gspread-pandas: https://pypi.org/project/gspread-pandas/
.. _pgsheets: https://pypi.org/project/pgsheets/
.. _PyDrive: https://pypi.org/project/PyDrive/

.. _MIT license: https://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://img.shields.io/pypi/v/gsheets.svg
    :target: https://pypi.org/project/gsheets/
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/gsheets.svg
    :target: https://pypi.org/project/gsheets/
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/gsheets.svg
    :target: https://pypi.org/project/gsheets/
    :alt: Supported Python Versions
.. |Format| image:: https://img.shields.io/pypi/format/gsheets.svg
    :target: https://pypi.org/project/gsheets/
    :alt: Format

.. |Build| image:: https://github.com/xflr6/gsheets/actions/workflows/build.yaml/badge.svg?branch=master
    :target: https://github.com/xflr6/gsheets/actions/workflows/build.yaml?query=branch%3Amaster
    :alt: Build
.. |Codecov| image:: https://codecov.io/gh/xflr6/gsheets/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/xflr6/gsheets
    :alt: Codecov
.. |Readthedocs-stable| image:: https://readthedocs.org/projects/gsheets/badge/?version=stable
    :target: https://gsheets.readthedocs.io/en/stable/?badge=stable
    :alt: Readthedocs stable
.. |Readthedocs-latest| image:: https://readthedocs.org/projects/gsheets/badge/?version=latest
    :target: https://gsheets.readthedocs.io/en/latest/?badge=latest
    :alt: Readthedocs latest