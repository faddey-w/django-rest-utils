# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_auto_20150703_1051'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeeplyNestedEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('int_data', models.IntegerField()),
                ('str_data', models.CharField(max_length=10)),
                ('parent', models.ForeignKey(related_name=b'nested', to='application.NestedEntity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
