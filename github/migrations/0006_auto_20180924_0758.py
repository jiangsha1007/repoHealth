# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-09-24 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('github', '0005_auto_20180919_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_org_info',
            name='create_time',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user_org_info',
            name='update_time',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user_org_info',
            name='user_type',
            field=models.IntegerField(default=0),
        ),
    ]
