
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination

from .models import NestedEntity, PrimaryEntity, DeeplyNestedEntity
from .serializers import PrimaryEntitySerializer, NestedEntitySerializer, DeeplyNestedEntitySerializer


class DeeplyNestedViewSet(ListModelMixin,
                          RetrieveModelMixin,
                          CreateModelMixin,
                          GenericViewSet):

    queryset = DeeplyNestedEntity.objects.all()
    serializer_class = DeeplyNestedEntitySerializer
    pagination_class = LimitOffsetPagination


class NestedViewSet(DeeplyNestedViewSet):

    nested_viewsets = {
        'bar': {
            'viewset': DeeplyNestedViewSet,
            'uses_kwargs': ['arg_one'],
        }
    }

    queryset = NestedEntity.objects.all()
    serializer_class = NestedEntitySerializer


class PrimaryViewSet(NestedViewSet):
    nested_viewsets = {
        'foo': {
            'viewset': NestedViewSet,
            'uses_kwargs': ['arg_one', 'arg_two'],
        }
    }

    queryset = PrimaryEntity.objects.all()
    serializer_class = PrimaryEntitySerializer
    pagination_class = LimitOffsetPagination
