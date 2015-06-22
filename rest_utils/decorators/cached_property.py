__author__ = 'faddey'

from functools import wraps
from django.utils.decorators import available_attrs


class read_only_cached_property(object):

    def __init__(self, fget=None, doc=None, name=None):
        self.getter(fget)
        self.name = getattr(fget, '__name__', name)
        assert isinstance(self.name, str), 'Cannot resolve property name'
        self.__doc__ = doc or fget.__doc__

    def getter(self, function):
        self.fget = function
        return self

    def setter(self, function):
        return read_write_cached_property(
            fget=self.fget,
            fset=function,
            doc=self.__doc__
        )

    def deleter(self, function):
        return read_write_cached_property(
            fget=self.fget,
            fdel=function,
            doc=self.__doc__
        )

    def invalidator(self, function):
        def wrapper(obj, *args, **kwargs):
            ret = function(obj, *args, **kwargs)
            self._invalidate(obj)
            return ret
        return wraps(function, assigned=available_attrs(function))(wrapper)

    def is_cached(self, obj):
        return self.name in obj.__dict__

    def _invalidate(self, obj):
        obj.__dict__.pop(self.name, None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        cached = self.fget(obj)
        obj.__dict__[self.name] = cached
        return cached


_empty = object()


class read_write_cached_property(read_only_cached_property):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, name=None):
        name = getattr(fset or fdel, '__name__', name)
        super(read_write_cached_property, self).__init__(fget, doc, name)
        self.setter(fset)
        self.deleter(fdel)

    def setter(self, function):
        self.fset = function
        return self

    def deleter(self, function):
        self.fdel = function
        return self

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cached = obj.__dict__.get(self.name, _empty)
        if cached is _empty:
            cached = super(read_write_cached_property, self).__get__(obj, objtype)
        return cached

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)
        self._invalidate(obj)

    def __delete__(self, obj):
        if self.fdel:
            self.fdel(obj)
        self._invalidate(obj)


def cached_property(fget=None, fset=None, fdel=None, doc=None, name=None):
    if fset or fdel:
        return read_write_cached_property(fget, fset, fdel, doc, name)
    else:
        return read_only_cached_property(fget, doc, name)
