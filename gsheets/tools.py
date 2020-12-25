# tools.py - generic helpers

import collections

__all__ = ['lazyproperty',
           'doctemplate',
           'list_view',
           'eval_source',
           'uniqued']


class lazyproperty(object):  # noqa: N801
    """Non-data descriptor caching the computed result as instance attribute.

    >>> class Spam(object):
    ...     @lazyproperty
    ...     def eggs(self):
    ...         return 'spamspamspam'

    >>> spam=Spam(); spam.eggs
    'spamspamspam'

    >>> spam.eggs='eggseggseggs'; spam.eggs
    'eggseggseggs'

    >>> Spam().eggs
    'spamspamspam'

    >>> Spam.eggs  # doctest: +ELLIPSIS
    <...lazyproperty object at 0x...>
    """

    def __init__(self, fget):
        self.fget = fget
        for attr in ('__module__', '__name__', '__doc__'):
            setattr(self, attr, getattr(fget, attr))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = instance.__dict__[self.__name__] = self.fget(instance)
        return result


def doctemplate(*args):
    """Return a decorator putting ``args`` into the docstring of the decorated ``func``.

    >>> @doctemplate('spam', 'spam')
    ... def spam():
    ...     '''Returns %s, lovely %s.'''
    ...     return 'Spam'

    >>> spam.__doc__
    'Returns spam, lovely spam.'
    """
    def decorator(func):
        func.__doc__ = func.__doc__ % tuple(args)
        return func
    return decorator


class list_view(object):  # noqa: N801
    """Readonly view on a list or sequence.

    >>> list_view(['spam'])
    ['spam']
    """

    def __init__(self, items):
        self._items = items

    def __repr__(self):
        return repr(self._items)

    def __len__(self):
        """Return the list size.

        >>> len(list_view(['spam']))
        1
        """
        return len(self._items)

    def __iter__(self):
        """Yield list items.

        >>> list(list_view(['spam']))
        ['spam']
        """
        return iter(self._items)

    def __contains__(self, item):
        """List member check.

        >>> 'spam' in list_view(['spam'])
        True
        """
        return item in self._items

    def __getitem__(self, index):
        """Member/slice retrieval.

        >>> list_view(['spam'])[0]
        'spam'
        """
        return self._items[index]


def group_dict(items, keyfunc):
    """Return a list defaultdict with ``items`` grouped by ``keyfunc``.

    >>> sorted(group_dict('eggs', lambda x: x).items())
    [('e', ['e']), ('g', ['g', 'g']), ('s', ['s'])]
    """
    result = collections.defaultdict(list)
    for i in items:
        key = keyfunc(i)
        result[key].append(i)
    return result


def eval_source(source):
    """Return ``eval(source)`` with ``source`` attached as attribute.

    >>> eval_source("lambda: 'spam'")()
    'spam'

    >>> eval_source("lambda: 'spam'").source
    "lambda: 'spam'"
    """
    result = eval(source)
    result.source = source
    return result


def uniqued(iterable):
    """Return unique list of ``iterable`` items preserving order.

    >>> uniqued('spameggs')
    ['s', 'p', 'a', 'm', 'e', 'g']
    """
    seen = set()
    return [item for item in iterable if item not in seen and not seen.add(item)]
