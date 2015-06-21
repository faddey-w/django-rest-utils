__author__ = 'faddey'

from functools import wraps

from django.utils.decorators import available_attrs


class RaiseOnFalseDecorator(object):

    def __new__(cls, function, *args, **kwargs):
        inst = super(RaiseOnFalseDecorator, cls).__new__(cls)
        # inst = super(RaiseOnFalseDecorator, cls).__new__(cls, function, *args, **kwargs)
        return wraps(function, assigned=available_attrs(function))(inst)

    def __init__(self, function, exc_class, default_raises, kwarg, pass_kwarg):
        self.wrapped = function
        self.exc_class = exc_class
        self.default_raises = default_raises
        self.kwarg_name = kwarg
        self.kwarg_getter = dict.get if pass_kwarg else dict.pop
        self.false_handler = lambda *args, **kwargs: ((), {})

    @classmethod
    def make_decorator(cls, exc_class, default_raises, kwarg, pass_kwarg):
        def decorator(function):
            return cls(function, exc_class, default_raises, kwarg, pass_kwarg)
        return decorator

    def __call__(self, *args, **kwargs):
        raise_exception = self.kwarg_getter(
            kwargs,
            self.kwarg_name,
            self.default_raises,
        )
        ret = self.wrapped(*args, **kwargs)
        if not self.check_result(ret) and raise_exception:
            self.handle_false(*args, **kwargs)

    def check_result(self, result):
        return bool(result)

    def handle_false(self, *args, **kwargs):
        exc_args, exc_kwargs = self.false_handler(*args, **kwargs)
        raise self.exc_class(*exc_args, **exc_kwargs)

    def on_exception(self, false_handler):
        self.false_handler = false_handler


def raise_on_false(exc_class=Exception,
                   default_raises=False,
                   pass_kwarg=False,
                   kwarg='raise_exception'):
    return RaiseOnFalseDecorator.make_decorator(
        exc_class=exc_class,
        default_raises=default_raises,
        kwarg=kwarg,
        pass_kwarg=pass_kwarg
    )


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
