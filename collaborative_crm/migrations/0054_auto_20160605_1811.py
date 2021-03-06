# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-05 21:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collaborative_crm', '0053_notificationtype_is_massive'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='T\xedtulo')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Creada')),
            ],
        ),
        migrations.CreateModel(
            name='ConversationUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Conversation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(default='', max_length=4000, verbose_name='Contenido')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Conversation')),
                ('user_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_from', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageUserTo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen', models.DateTimeField(blank=True, null=True, verbose_name='Visto')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collaborative_crm.Message')),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='users_to',
            field=models.ManyToManyField(related_name='users_to', through='collaborative_crm.MessageUserTo', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='conversation',
            name='users',
            field=models.ManyToManyField(through='collaborative_crm.ConversationUser', to=settings.AUTH_USER_MODEL),
        ),
    ]
