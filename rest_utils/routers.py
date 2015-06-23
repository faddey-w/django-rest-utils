__author__ = 'faddey'

from rest_framework.routers import DefaultRouter
from rest_framework.decorators import detail_route, list_route


class ModifiableRouterMixin(object):

    _routes = list(DefaultRouter.routes)

    @property
    def routes(self):
        return self._routes

    @property
    def list_route(self):
        return self.routes[0]

    @property
    def detail_route(self):
        return self.routes[2]


class ModifiableRouter(ModifiableRouterMixin, DefaultRouter):
    pass
