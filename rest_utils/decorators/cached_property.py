__author__ = 'faddey'

from functools import wraps
from django.utils.decorators import available_attrs


def _make_getter(prop, fget):
    if fget:
        def getter(self):
            cached = fget(self)
            self.__dict__[prop.name] = cached
            return cached
        return getter
    else:
        return None


def _make_setter(prop, fset):
    if fset:
        def setter(self, value):
            fset(self, value)
            prop._invalidate(self)
        return setter
    else:
        return None


def _make_deleter(prop, fdel):
    if fdel:
        def deleter(self):
            fdel(self)
            prop._invalidate(self)
        return deleter
    else:
        return None


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

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return self
        if not self.fget:
            raise AttributeError('Cannot read attribute {}'.format(self.name))
        if not self.is_cached(obj):
            value = super(cached_property, self).__get__(obj, obj_type)
            obj.__dict__[self.name] = value
        else:
            value = obj.__dict__[self.name]
        return value

    # def __set__(self, obj, value):
    #     return super(cached_property, self).__set__(obj, value)

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
