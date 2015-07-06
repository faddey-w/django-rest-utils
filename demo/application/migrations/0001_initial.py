# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NestedEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('int_data', models.IntegerField()),
                ('str_data', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrimaryEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('int_primary', models.IntegerField()),
                ('str_primary', models.CharField(max_length=10)),
                ('nested', models.ForeignKey(to='application.NestedEntity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
