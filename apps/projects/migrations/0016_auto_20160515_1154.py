# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-15 06:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_auto_20160515_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='release_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 18, 11, 54, 57, 80134)),
        ),
    ]
