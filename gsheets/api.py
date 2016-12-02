# api.py - library user interface

"""Main interface for the library user."""

from . import oauth2, backend, models, urls, tools

__all__ = ['Sheets']

# TODO: get worksheet


class Sheets(object):
    """Collection of spreadsheets available from given OAuth 2.0 credentials."""

    @classmethod
    @tools.doctemplate(oauth2.SECRETS, oauth2.STORAGE, oauth2.SCOPES)
    def from_files(cls, secrets=None, storage=None, scopes=None, no_webserver=False):
        """Return a spreadsheet collection making OAauth 2.0 credentials.

        Args:
            secrets (str): location of secrets file (default: %r)
            storage (str): location of storage file (default: %r)
            scopes: scope URL(s) or 'read' or 'write' (default: %r)
            no_webserver (bool): URL/code prompt instead of webbrowser auth
        Returns:
            Sheets: new Sheets instance with OAauth 2.0 credentials
        """
        creds = oauth2.get_credentials(scopes, secrets, storage, no_webserver)
        return cls(creds)

    def __init__(self, credentials):
        self._creds = credentials

    @tools.lazyproperty
    def _sheets(self):
        """Google sheets API service endpoint (v4)."""
        return backend.build_service('sheets', credentials=self._creds)

    @tools.lazyproperty
    def _drive(self):
        """Google drive API service endpoint (v3)."""
        return backend.build_service('drive', credentials=self._creds)

    def __len__(self):
        """Return the number of available spreadsheets.

        Returns:
            int: number of spreadsheets
        """
        return sum(1 for _ in backend.iterfiles(self._drive))

    def __iter__(self):
        """Fetch and yield all available spreadsheets.

        Yields:
            new SpreadSheet spreadsheet instances
        """
        return (self[id] for id, title in backend.iterfiles(self._drive))

    def __contains__(self, id):
        """Return if there is a spreadsheet with the given id.

        Args:
            id (str): unique alphanumeric id of the spreadsheet
        Returns:
            bool: True if it can be fetched else False
        """
        try:
            backend.spreadsheet(self._sheets, id)
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, id):
        """Fetch and return the spreadsheet with the given id.

        Args:
            id (str): unique alphanumeric id of the spreadsheet
        Returns:
            SpreadSheet: new SpreadSheet instance
        Raises:
            KeyError: if no spreadsheet with the given id is found
        """
        if id == slice(None, None):
            return list(self)
        response = backend.spreadsheet(self._sheets, id)
        result = models.SpreadSheet._from_response(response, self._sheets)
        result._api = self
        return result

    def get(self, id_or_url, default=None):
        """Fetch and return the spreadsheet with the given id or url.

        Args:
            id_or_url (str): unique alphanumeric id or URL of the spreadsheet
        Returns:
            New SpreadSheet instance or given default if none is found
        Raises:
            ValueError: if an URL is given from which no id could be extracted
        """
        if '/' in id_or_url:
            id = urls.SheetUrl.from_string(id_or_url).id
        else:
            id = id_or_url
        try:
            return self[id]
        except KeyError:
            return default

    def find(self, title):
        """Fetch and return the first spreadsheet with the given title.

        Args:
            title(str): title/name of the spreadsheet to return
        Returns:
            SpreadSheet: new SpreadSheet instance
        Raises:
            KeyError: if no spreadsheet with the given title is found
        """
        files = backend.iterfiles(self._drive, name=title)
        try:
            return next(self[id] for id, name in files)
        except StopIteration:
            raise KeyError(title)

    def findall(self, title=None):
        """Fetch and return a list of spreadsheets with the given title.

        Args:
            title(str): title/name of the spreadsheets to return, or None for all
        Returns:
            list: list of new SpreadSheet instances (possibly empty)
        """
        if title is None:
            return list(self)
        files = backend.iterfiles(self._drive, name=title)
        return [self[id] for id, name in files]

    def iterfiles(self):
        """Yield (id, title) pairs for all available spreadsheets.

        Yields:
            pairs of unique id (str) and title/name (str)
        """
        return backend.iterfiles(self._drive)

    def ids(self):
        """Return a list of all available spreadsheet ids.

        Returns:
            list: list of unique alphanumeric id strings
        """
        return [id for id, name in self.iterfiles()]

    def titles(self, unique=False):
        """Return a list of all available spreadsheet titles.

        Args:
            unique (bool): drop duplicates
        Returns:
            list: list of title/name strings
        """
        if unique:
            return tools.uniqued(title for id, title in self.iterfiles())
        return [title for id, title in self.iterfiles()]
