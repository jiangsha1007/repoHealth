# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-10-02 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('github', '0011_auto_20180928_0613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_org_info',
            name='branches_count',
        ),
        migrations.RemoveField(
            model_name='user_org_info',
            name='pulls_count',
        ),
        migrations.AddField(
            model_name='repo_base_info',
            name='repo_branch_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user_org_info',
            name='user_type',
            field=models.CharField(max_length=100),
        ),
    ]
