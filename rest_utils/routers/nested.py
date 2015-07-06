"""
Implementation notes
"""  # TODO add implementation notes
__author__ = 'faddey'

import inspect
import re
from collections import namedtuple

from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSetMixin

from ..functions import safecall


NestedViewSetInfo = namedtuple('NestedViewSetInfo', ['viewset', 'base_name', 'detail', 'uses_kwargs'])

_lookup_kwarg_regex = re.compile(r'^__nested_lookup(?P<depth>\d+)$')

def _get_depth(kwarg_name):
    m = re.match(_lookup_kwarg_regex, kwarg_name)
    if m:
        return int(m.groupdict()['depth'])
    return None

def _get_parent(viewset):
    parent_attr_name = getattr(viewset, 'parent_attr_name', None)
    if parent_attr_name:
        return getattr(viewset, parent_attr_name, None)
    return None

def _build_parents_seq(nested_viewset, attr_name):
    current_parent = _get_parent(nested_viewset)
    parents = []
    while current_parent:
        parents.insert(0, current_parent())
        current_parent = _get_parent(current_parent.viewset)
    for index, parent in enumerate(parents[1:], 1):
        setattr(parent, attr_name, parents[index-1])
    return parents

def _get_lookup_kwarg(viewset):
    lookup_field = getattr(viewset, 'lookup_field', 'pk')
    return getattr(viewset, 'lookup_url_kwarg', None) or lookup_field


class NestedViewSetMixin(object):

    def dispatch(self, request, *args, **kwargs):

        lookup_kwargs = {
            depth: kwarg
            for depth, kwarg in [
                (_get_depth(kw), kw)
                for kw in kwargs
                ]
            if depth is not None
            }
        parents = _build_parents_seq(self, self.parent_attr_name)

        for depth, parent in enumerate(parents):
            viewset = parent.viewset
            lookup_name = lookup_kwargs.get(depth)
            if lookup_name:
                setattr(parent, viewset._nested_lookup_url_kwarg, kwargs[lookup_name])
            for kwarg in viewset._uses_kwargs:
                setattr(parent, kwarg, kwargs[kwarg])

        setattr(self, self.parent_attr_name, parents[-1])

        passed_kwargs = {}
        self_depth = len(parents)
        self_lookup_kwarg = lookup_kwargs.get(self_depth)
        if self_lookup_kwarg:
            passed_kwargs[self._nested_lookup_url_kwarg] = kwargs[self_lookup_kwarg]
        for kwarg in self._uses_kwargs:
            passed_kwargs[kwarg] = kwargs[kwarg]
        self.lookup_url_kwarg = self._nested_lookup_url_kwarg
        return super(NestedViewSetMixin, self).dispatch(request, *args, **passed_kwargs)

    @classmethod
    def has_parent(cls):
        return bool(_get_parent(cls))


class NestingRouterMixin(object):

    """
    This mixin used for creating routers that supports nested resources,
    i.e. urls like "/post/123/comment/1532/".

    For usage example you can see demo django project at branch "feature_nested_resources"
    in my github repo
    """  # TODO add reference to repo

    nested_views_router_class = DefaultRouter
    parent_attr_name = 'parent'

    def __init__(self, parent_viewsets=(), *args, **kwargs):
        self.parent_viewsets = parent_viewsets
        super(NestingRouterMixin, self).__init__(*args, **kwargs)

    @property
    def depth(self):
        return len(self.parent_viewsets)

    def get_nested_urls(self, viewset):
        nested_viewsets = getattr(viewset, 'nested_viewsets', None)
        if not nested_viewsets:
            return []

        if not issubclass(viewset, NestedViewSetMixin):
            viewset = self.wrap_nested_viewset(viewset)

        nested_router = self.create_nested_router(viewset)
        for node_name, entry in nested_viewsets.items():
            entry = self._parse_entry(node_name, entry)
            wrapped_viewset = self.wrap_nested_viewset(
                entry.viewset,
                viewset,
                entry.uses_kwargs,
            )

            prefix = node_name
            if entry.detail:
                prefix = self.get_lookup_regex(
                    viewset=viewset,
                    lookup_kwarg=viewset.lookup_url_kwarg
                ) + '/' + prefix

            nested_router.register(prefix, wrapped_viewset, entry.base_name)

        return nested_router.urls

    def create_nested_router(self, viewset):
        if issubclass(self.nested_views_router_class, NestingRouterMixin):
            parents = self.parent_viewsets + (viewset,)
            nested_router = self.nested_views_router_class(parents)
        else:
            nested_router = self.nested_views_router_class()
        if isinstance(nested_router, DefaultRouter):
            nested_router.include_root_view = False
        return nested_router

    def wrap_nested_viewset(self, viewset, parent_viewset=None, uses_kwargs=(), **extra_fields):

        lookup_field = getattr(viewset, 'lookup_field', 'pk')
        nested_lookup_url_kwarg = getattr(viewset, 'lookup_url_kwarg', None) or lookup_field

        depth = (self.depth + 1) if parent_viewset else self.depth
        lookup_url_kwarg = '__nested_lookup' + str(depth)

        class_name = 'Nested' + viewset.__name__
        bases = (NestedViewSetMixin, viewset)
        dictionary = {
            '_uses_kwargs': tuple(uses_kwargs),
            '_nested_lookup_url_kwarg': nested_lookup_url_kwarg,
            'lookup_url_kwarg': lookup_url_kwarg,
        }
        if parent_viewset:
            parent = self.make_parent_class(
                viewset,
                uses_kwargs,
                **extra_fields
            )
            parent.viewset = parent_viewset
            dictionary.update({
                self.parent_attr_name: parent,
                'parent_attr_name': self.parent_attr_name,
            })
        dictionary.update(extra_fields)
        wrapped_viewset = type(class_name, bases, dictionary)
        return wrapped_viewset

    def make_parent_class(self, viewset, uses_kwargs, **extra_fields):
        return type(viewset.__name__ + 'Parent', (), {})

    def _parse_entry(self, node_name, entry):
        if isinstance(entry, NestedViewSetInfo):
            return entry
        if inspect.isclass(entry) and issubclass(entry, ViewSetMixin):
            ret = NestedViewSetInfo(
                viewset=entry,
                base_name=safecall(self.get_default_base_name, entry) or node_name,
                detail=True,
                uses_kwargs=(),
            )
        else:
            kwargs = {
                'base_name': safecall(self.get_default_base_name, entry['viewset']) or node_name,
                'detail': True,
                'uses_kwargs': (),
            }
            kwargs.update(entry)
            ret = NestedViewSetInfo(**kwargs)
        return ret

    def get_urls(self):
        urls = super(NestingRouterMixin, self).get_urls()

        nested_urls = []
        for prefix, viewset, basename in self.registry:
            regex = r'^{}/'.format(prefix)
            nested_urls.append(url(
                regex,
                include(self.get_nested_urls(viewset))
            ))
        nested_urls.extend(urls)

        return nested_urls

    def get_lookup_regex(self, viewset, lookup_prefix='', lookup_kwarg=None):
        """
        Given a viewset, return the portion of URL regex that is used
        to match against a single instance.

        Note that lookup_prefix is not used directly inside REST rest_framework
        itself, but is required in order to nicely support nested router
        implementations, such as drf-nested-routers.

        https://github.com/alanjds/drf-nested-routers
        """
        base_regex = '(?P<{lookup_prefix}{lookup_url_kwarg}>{lookup_value})'
        # Use `pk` as default field, unset set.  Default regex should not
        # consume `.json` style suffixes and should break at '/' boundaries.
        lookup_url_kwarg = lookup_kwarg or _get_lookup_kwarg(viewset)
        lookup_value = getattr(viewset, 'lookup_value_regex', '[^/.]+')
        return base_regex.format(
            lookup_prefix=lookup_prefix,
            lookup_url_kwarg=lookup_url_kwarg,
            lookup_value=lookup_value
        )


class NestingRouter(NestingRouterMixin, DefaultRouter):
    pass


class RecursiveRouter(NestingRouter):
    pass
RecursiveRouter.nested_views_router_class = RecursiveRouter
