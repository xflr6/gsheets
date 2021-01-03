# urls.py - parse and generate spreadsheet urls

"""Spreadsheet and worksheet URLs."""

import re

__all__ = ['SheetUrl']


class SheetUrl(object):
    """URL for (the first or another) sheet of a Google docs spreadsheet."""

    _pattern = re.compile(r'/spreadsheets/d/(?P<id>[a-zA-Z0-9-_]+)')

    _template = 'https://docs.google.com/spreadsheets/d/{id}/edit#gid={gid:d}'

    @classmethod
    def from_string(cls, link):
        """Return a new SheetUrl instance from parsed URL string.

        >>> SheetUrl.from_string('https://docs.google.com/spreadsheets/d/spam')
        <SheetUrl id='spam' gid=0>
        """
        ma = cls._pattern.search(link)
        if ma is None:
            raise ValueError(link)
        id = ma.group('id')
        return cls(id)

    def __init__(self, id, gid=0):
        """

        >>> SheetUrl('spam').id
        'spam'

        >>> SheetUrl('spam', 42).gid
        42
        """
        self.id = id
        self.gid = gid

    def __repr__(self):
        return f'<{self.__class__.__name__} id={self.id!r} gid={self.gid:d}>'

    def to_string(self, gid=None):
        """

        >>> SheetUrl('spam').to_string()
        'https://docs.google.com/spreadsheets/d/spam/edit#gid=0'

        >>> SheetUrl('spam').to_string(42)
        'https://docs.google.com/spreadsheets/d/spam/edit#gid=42'
        """
        if gid is None:
            gid = self.gid
        return self._template.format(id=self.id, gid=gid)

    __str__ = to_string

    @property
    def short_id(self):
        """

        >>> SheetUrl('1234567890').short_id
        '1234567890'

        >>> SheetUrl('12345678901').short_id
        '12345...01'
        """
        if len(self.id) <= 10:
            return self.id
        return f'{self.id[:5]}...{self.id[-2:]}'
