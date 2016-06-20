# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-08 13:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collaborative_crm', '0057_changelogentrytype_requires_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInChargeUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_user', to=settings.AUTH_USER_MODEL)),
                ('user_in_charge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]