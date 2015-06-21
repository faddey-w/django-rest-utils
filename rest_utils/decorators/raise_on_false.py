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
