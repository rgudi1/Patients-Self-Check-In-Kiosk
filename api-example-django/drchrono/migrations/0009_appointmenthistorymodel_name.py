# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-14 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0008_auto_20170614_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmenthistorymodel',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]