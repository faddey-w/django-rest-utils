__author__ = 'faddey'

from rest_framework.serializers import ModelSerializer

from .models import PrimaryEntity, NestedEntity, DeeplyNestedEntity


class PrimaryEntitySerializer(ModelSerializer):

    class Meta:
        model = PrimaryEntity
        fields = ('id',
                  'int_primary',
                  'str_primary',
                  'nested',)

class NestedEntitySerializer(ModelSerializer):

    class Meta:
        model = NestedEntity
        fields = ('id',
                  'int_data',
                  'str_data',
                  'parent',)

class DeeplyNestedEntitySerializer(ModelSerializer):

    class Meta:
        model = DeeplyNestedEntity
        fields = ('id',
                  'int_data',
                  'str_data',
                  'parent',)
