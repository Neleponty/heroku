# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-27 18:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20160426_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='describe',
            field=models.CharField(default='', max_length=6000),
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=models.ImageField(default='', max_length=300, upload_to=''),
        ),
        migrations.AlterField(
            model_name='project',
            name='release_date',
            field=models.DateField(default=datetime.date(2016, 6, 26)),
        ),
        migrations.AlterField(
            model_name='project',
            name='title_video',
            field=models.FileField(blank=True, max_length=300, upload_to=''),
        ),
    ]
