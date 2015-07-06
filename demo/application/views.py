
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination

from .models import NestedEntity, PrimaryEntity, DeeplyNestedEntity
from .serializers import PrimaryEntitySerializer, NestedEntitySerializer, DeeplyNestedEntitySerializer

# For generated urlconf


class CreateReadViewSet(ListModelMixin,
                        RetrieveModelMixin,
                        CreateModelMixin,
                        GenericViewSet):

    pagination_class = LimitOffsetPagination


class DeeplyNestedViewSet(CreateReadViewSet):

    queryset = DeeplyNestedEntity.objects.all()
    serializer_class = DeeplyNestedEntitySerializer

    def retrieve(self, request, pk, arg_one):
        resp = super(DeeplyNestedViewSet, self).retrieve(request, pk, arg_one)
        resp['X-Arg-One'] = arg_one
        return resp


class NestedViewSet(CreateReadViewSet):

    nested_viewsets = {
        'bar': {
            'viewset': DeeplyNestedViewSet,
            'uses_kwargs': ['arg_one'],
        }
    }

    queryset = NestedEntity.objects.all()
    serializer_class = NestedEntitySerializer

    def retrieve(self, request, pk, arg_one, arg_two):
        resp = super(NestedViewSet, self).retrieve(request, pk, arg_one, arg_two)
        resp['X-Arg-One'] = arg_one
        resp['X-Arg-Two'] = arg_two
        return resp


class PrimaryViewSet(CreateReadViewSet):
    nested_viewsets = {
        'foo': {
            'viewset': NestedViewSet,
            'uses_kwargs': ['arg_one', 'arg_two'],
        }
    }

    queryset = PrimaryEntity.objects.all()
    serializer_class = PrimaryEntitySerializer
