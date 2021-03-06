# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-09-25 09:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('github', '0007_auto_20180925_0600'),
    ]

    operations = [
        migrations.RenameField(
            model_name='org_members_info',
            old_name='org_id',
            new_name='org',
        ),
        migrations.RenameField(
            model_name='repo_develop_info',
            old_name='repo_id',
            new_name='repo',
        ),
        migrations.RenameField(
            model_name='repo_developer_info',
            old_name='repo_id',
            new_name='repo',
        ),
        migrations.RenameField(
            model_name='repo_developer_info',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='repo_issue_info',
            old_name='repo_id',
            new_name='repo',
        ),
        migrations.RenameField(
            model_name='repo_issue_info',
            old_name='user_id',
            new_name='user',
        ),
    ]
