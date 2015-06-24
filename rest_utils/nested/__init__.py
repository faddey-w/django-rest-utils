__author__ = 'faddey'

from rest_framework.viewsets import GenericViewSet


class NestedViewSet(GenericViewSet):

    def dispatch(self, request, *args, **kwargs):
        pass