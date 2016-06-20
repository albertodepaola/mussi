#!/usr/bin/python
# -*- coding: utf-8 -*-

from channels import Channel, Group
from channels.auth import channel_session_user, channel_session_user_from_http
from models import User, Notification, notification_types, Company


@channel_session_user_from_http
def updates_connect(message):
    Group('updates-channel-user-%s' % message.user.id).add(message.reply_channel)


@channel_session_user
def updates_disconnect(message):
    Group('updates-channel-user-%s' % message.user.id).discard(message.reply_channel)


def notify_user(message):
    user = User.objects.get(id=int(message['user_id']))
    related_user = User.objects.get(id=int(message['related_user_id']))
    nc = user.notification_config(message['notification_type'])

    if nc.take_action:
        notification = Notification(user=user, type_id=notification_types[message['notification_type']],
                                    related_user=related_user, seen=not nc.notify, **message['data'])

    notification.save(only_if_should_notify=True, host_url=message['host_url'])

    if nc.email and message['host_url']:
        Channel('email_notification').send({
            'notification_id': notification.id,
            'host_url': message['host_url']
        })


def email_notification(message):
    notification = Notification.objects.filter(id=message['notification_id']).first()
    if notification:
        notification.email(message['host_url'])


def notify_company(message):
    company = Company.objects.get(id=int(message['company_id']))
    related_user = User.objects.get(id=int(message['related_user_id']))

    for user in company.users_with_massive_notifications(notification_type=message['notification_type']):
        user.notify(message['notification_type'], related_user, data=message['data'], host_url=message['host_url'])
