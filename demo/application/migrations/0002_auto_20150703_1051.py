# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='primaryentity',
            name='nested',
        ),
        migrations.AddField(
            model_name='nestedentity',
            name='parent',
            field=models.ForeignKey(related_name=b'nested', default=1, to='application.PrimaryEntity'),
            preserve_default=False,
        ),
    ]
