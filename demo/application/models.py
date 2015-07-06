from django.db import models


class PrimaryEntity(models.Model):

    int_primary = models.IntegerField()

    str_primary = models.CharField(max_length=10)

    def __repr__(self):
        return '<Primary entity: ' + ' '.join(
            key + '=' + value for key, value in [
                ('id', self.id),
                ('int_primary', self.int_primary),
                ('str_primary', self.str_primary),
            ]
        ) + '>'

class NestedEntity(models.Model):

    int_data = models.IntegerField()

    str_data = models.CharField(max_length=10)

    parent = models.ForeignKey(PrimaryEntity, related_name='nested')

    def __repr__(self):
        return '<Nested entity: ' + ' '.join(
            key + '=' + value for key, value in [
                ('id', self.id),
                ('int_data', self.int_data),
                ('str_data', self.str_data),
                ('parent', self.parent_id),
            ]
        ) + '>'

class DeeplyNestedEntity(models.Model):

    int_data = models.IntegerField()

    str_data = models.CharField(max_length=10)

    parent = models.ForeignKey(NestedEntity, related_name='nested')

    def __repr__(self):
        return '<DeeplyNested entity: ' + ' '.join(
            key + '=' + value for key, value in [
                ('id', self.id),
                ('int_data', self.int_data),
                ('str_data', self.str_data),
                ('parent', self.parent_id),
            ]
        ) + '>'
