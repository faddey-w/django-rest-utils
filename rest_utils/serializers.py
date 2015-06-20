class ModelBatchUpdateSerializer(serializers.Serializer):

    def __init__(self, instance=None, data=serializers.empty, **kwargs):

        self._init_kwargs = kwargs.copy()
        
        self._serializer_class = self._get_meta_info('serializer_class', kwargs)
        assert issubclass(self._serializer_class, serializers.ModelSerializer), (
            "Model serializer class must be specified in Meta or in kwarg 'serializer_class'."
        )
        self._pk_field = self._get_meta_info('pk_field', kwargs, 'id')
        self._model_class = self._serializer_class.Meta.model
        self._serializer_kwargs = self._get_meta_info('serializer_kwargs', kwargs, {})

        self._declared_fields.update({
            'to_create': self._serializer_class(
                many=True,
                required=False,
                **self._serializer_kwargs
            ),
            'to_update': self._serializer_class(
                many=True,
                partial=True,
                required=False,
                **self._serializer_kwargs
            ),
            'to_delete': serializers.ListField(
                child=serializers.IntegerField(),
                required=False
            )
        })

        super(ModelBatchUpdateSerializer, self).__init__(None, data, **kwargs)

    def __new__(cls, instance=None, data=serializers.empty, **kwargs):
        # import pdb; pdb.set_trace()
        if instance:
            read_serializer_class = cls._get_meta_info(
                'serializer_class',
                kwargs
            )
            kwargs.pop('serializer_class', None)
            kwargs.pop('serializer_kwargs', None)
            kwargs.pop('pk_field', None)
            return read_serializer_class(instance, data, **kwargs)
        else:
            return super(ModelBatchUpdateSerializer, cls).__new__(
                cls, instance, data, **kwargs
            )

    @classmethod
    def _get_meta_info(cls, key, kwargs, default=None):
        info = kwargs.pop(key, None)
        if not info:
            meta = getattr(cls, 'Meta', None)
            info = getattr(meta, key, default)
        return info

    @property
    def fields(self):
        if self.instance:
            return {}
        else:
            if not hasattr(self, '_fields'):
                self._fields = {}
                for key, field in self.get_fields().items():
                    field.bind(
                        field_name=key,
                        parent=None
                    )
                    self._fields[key] = field
            return self._fields

    def validate_to_delete(self, validated_data):
        missing_ids = self._find_missing_ids(validated_data)
        if missing_ids:
            missing_ids = sorted(missing_ids)
            raise ValidationError(
                "Instances with ID " + ' '.join(map(str, missing_ids))
                + " not found. Cannot delete them."
            )
        return validated_data

    def validate_to_update(self, validated_data):
        ids = filter(bool, (e.get('id') for e in validated_data))
        missing_ids = self._find_missing_ids(ids)
        if missing_ids:
            missing_ids = sorted(missing_ids)
            raise ValidationError(
                "Instances with ID " + ' '.join(map(str, missing_ids))
                + " not found. Cannot update them."
            )
        return validated_data

    def _find_missing_ids(self, tested_ids):
        tested_ids = set(tested_ids)

        lookup = self._pk_field + '__in'

        ids = list(
            self._model_class.objects
                .values(
                    self._pk_field
                ).filter(
                    **{lookup: tested_ids}
                )
        )
        ids = set(
            entry[self._pk_field]
            for entry in ids
        )

        if len(ids) != len(tested_ids):
            return tested_ids - ids
        else:
            return set()

    def get_delete_lookup(self):
        return self._pk_field + '__in'

    def save(self, **kwargs):
        assert not hasattr(self, 'save_object'), (
            'Serializer `%s.%s` has old-style version 2 `.save_object()` '
            'that is no longer compatible with REST framework 3. '
            'Use the new-style `.create()` and `.update()` methods instead.' %
            (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        validated_data = dict(self.validated_data)

        with transaction.atomic():
            for entry in validated_data.get('to_create', []):
                entry.update(kwargs)
                self._model_class.objects.create(**entry)
            for entry in validated_data.get('to_update', []):
                entry.update(kwargs)
                instance = self._model_class(**entry)
                entry.pop('id')
                instance.save(update_fields=entry.keys())

            lookup = self.get_delete_lookup()
            self._model_class.objects.filter(
                **{
                    lookup: validated_data.get('to_delete', [])
                }
            ).delete()

    def get_attribute(self, instance):
        attribute = super(ModelBatchUpdateSerializer, self).get_attribute(instance)
        self.instance = attribute
        return attribute

    def to_representation(self, instance):
        kwargs = self._init_kwargs
        kwargs['many'] = True
        return self.__class__(
            instance,
            getattr(self, 'initial_data', serializers.empty),
            **kwargs
        ).to_representation(instance)