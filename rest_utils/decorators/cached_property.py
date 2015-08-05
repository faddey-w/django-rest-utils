__author__ = 'faddey'

from functools import wraps
from django.utils.decorators import available_attrs


def _make_getter(prop, fget):
    def getter(self):
        cached = fget(self)
        self.__dict__[prop.name] = cached
        return cached
    return getter


def _make_setter(prop, fset):
    def setter(self, value):
        fset(self, value)
        prop._invalidate(self)
    return setter


def _make_deleter(prop, fdel):
    def deleter(self):
        fdel(self)
        prop._invalidate(self)
    return deleter


class cached_property(property):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, name=None):
        resolved_name = name
        for function in [fget, fset, fdel]:
            if function:
                resolved_name = getattr(function, '__name__', None)
                if resolved_name and resolved_name != '<lambda>':
                    break
        assert isinstance(resolved_name, str), 'Cannot resolve property name'
        self.name = resolved_name
        super(cached_property, self).__init__(
            fget=_make_getter(self, fget),
            fset=_make_setter(self, fset),
            fdel=_make_deleter(self, fdel),
            doc=doc,
        )

    # def getter(self, function):
    #     return super(cached_property, self).getter(_make_getter(self, function))
    #
    # def setter(self, function):
    #     return super(cached_property, self).setter(_make_setter(self, function))
    #
    # def deleter(self, function):
    #     return super(cached_property, self).deleter(_make_deleter(self, function))

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
