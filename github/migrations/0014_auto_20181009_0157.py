# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-10-09 01:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('github', '0013_auto_20181003_0759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repo_develop_info',
            name='command_count_permonth',
        ),
        migrations.RemoveField(
            model_name='repo_develop_info',
            name='issue_command_count_permonth',
        ),
        migrations.RemoveField(
            model_name='repo_develop_info',
            name='issue_count_permonth',
        ),
    ]
