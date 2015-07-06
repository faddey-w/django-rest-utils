__author__ = 'faddey'

from django.views.generic import View

from rest_framework.decorators import detail_route, list_route


def safecall(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except:
        return None


def detail_endpoint(view_class, methods=None, initkwargs=None, route_kwargs=None):
    return endpoint(view_class, detail_route, methods, initkwargs, route_kwargs)

def list_endpoint(view_class, methods=None, initkwargs=None, route_kwargs=None):
    return endpoint(view_class, list_route, methods, initkwargs, route_kwargs)

def endpoint(view_class, decorator, methods=None, initkwargs=None, route_kwargs=None):
    initkwargs = initkwargs or {}
    route_kwargs = route_kwargs or {}
    view = view_class.as_view(**initkwargs)
    methods = methods or [m for m in View.http_method_names if hasattr(view_class, m)]
    return decorator(methods, **route_kwargs)(view)
