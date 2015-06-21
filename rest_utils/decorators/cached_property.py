__author__ = 'faddey'

_empty = object()


class cached_property(object):

    _cached_values = {}

    def getter(self, function):
        if function:
            def fget(obj, type=None):
                cached = self._cached_values.get(id(obj), _empty)
                if cached is _empty:
                    cached = function(obj)
                    self._cached_values[id(obj)] = cached
                return cached
            self.fget = fget
        else:
            self.fget = None
        return self

    def setter(self, function):
        if function:
            def fset(obj, value):
                self._cached_values[id(obj)] = _empty
                return function(obj, value)
            self.fset = fset
        else:
            self.fset = None
        return self

    def deleter(self, function):
        def fdel(obj):
            self._cached_values[id(obj)] = _empty
            if function:
                return function(obj)
        self.fdel = fdel
        return self

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.getter(fget)
        self.setter(fset)
        self.deleter(fdel)
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
