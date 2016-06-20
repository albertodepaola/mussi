#!/usr/bin/python
# -*- coding: utf-8 -*-

from ..models import utc_to_local, Contact, Property, User, Conversation
from django import template
import collections

register = template.Library()


@register.filter
def utc_to_local_tz(value, format):
    return utc_to_local(value).strftime(format) if value is not None and value != '' else None


@register.filter
def dict_to_html_attributes(value):
    return reduce(lambda html_string, attribute: html_string + ' ' + attribute.replace(u' ', u'-')
                  .replace(u'_', u'-') + u'="{0}"'.format(unicode(value[attribute]).replace(u'"', u'')),
                  value.keys(), u'').strip()


@register.filter
def is_owner(value, property):
    if value is None or property is None:
        return False
    if value.__class__ != Contact or property.__class__ != Property:
        raise ValueError('\'is_owner\' is to be used for a Contact and a Property object')
    return value.is_owner(property)


@register.filter
def is_interested(value, property):
    if value is None or property is None:
        return False
    if value.__class__ != Contact or property.__class__ != Property:
        raise ValueError('\'is_interested\' is to be used for a Contact and a Property object')
    return value.is_interested(property)


@register.filter
def notification_type_config(value, notification_type_id):
    if value.__class__ != User or notification_type_id.__class__ != int:
        raise ValueError('\'notification_type_config\' is to be used for a User and a notification_type_id (int)')
    return value.notification_config(None, id=notification_type_id)


@register.filter
def name_me(value, user):
    if value.__class__ != User or user.__class__ != User:
        raise ValueError('\'name_me\' is to be used for a User and a notification_type_id (int)')
    return value.full_name if value != user else u'Yo'


@register.filter
def name_me_reversed(value, user):
    if value.__class__ != User or user.__class__ != User:
        raise ValueError('\'name_me_reversed\' is to be used for a User and a notification_type_id (int)')
    return value.full_name_reversed if value != user else u'Yo'


@register.filter
def sort_by(value, sort_key):
    if not isinstance(value, collections.Iterable) or unicode(sort_key).__class__ not in [str, unicode]:
        raise ValueError('\'sort_by\' is to be used for iterable objects and sort_key should be one of \'str\', '
                         '\'unicode\'')
    reverse = False
    if sort_key[0] == '-':
        sort_key = sort_key[1:]
        reverse = True
    return sorted(value, key=lambda elem: eval('elem.{0}'.format(sort_key)), reverse=reverse)


@register.filter
def unred_messages(value, user):
    if value.__class__ != Conversation or user.__class__ != User:
        raise ValueError('\'unred_messages\' is to be used for a Conversation and a User objects')
    return value.unred_messages(user)


@register.filter
def class_name(value):
    return value.__class__.__name__


@register.filter
def full_name_with_text_search_matches(value, search_term):
    if value.__class__ not in [User, Contact, Property] or search_term.__class__ not in [str, unicode]:
        raise ValueError('\'full_name_with_text_search_matches\' is to be used for a User, Property or Contact object '
                         'value with a str or unciode search_term parameter')

    return value.full_name_with_text_search_matches(search_term)


@register.filter
def email_with_text_search_matches(value, search_term):
    if value.__class__ not in [User, Contact] or search_term.__class__ not in [str, unicode]:
        raise ValueError('\'email_with_text_search_matches\' is to be used for a User or Contact object value with a '
                         'str or unciode search_term parameter')

    return value.email_with_text_search_matches(search_term)


@register.filter
def permissions_over(value, obj):
    if value.__class__ != User or obj.__class__ not in [User, Property, Contact]:
        raise ValueError('\'permissions_over\' is to be used with a User and a Contact or Property or other User '
                         'objects')

    if obj.__class__ == Contact:
        return value.permissions_over_contact(obj)
    if obj.__class__ == Property:
        return value.permissions_over_property(obj)
    if obj.__class__ == User:
        return value.permissions_over_user(obj)

    return False


@register.filter
def currency(value, currency=None):
    if value and value != u'-':
        return u'{0} {1}'.format(currency if currency else '$', value)

    return value


@register.filter
def negate(value):
    return not value

