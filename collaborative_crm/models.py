#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.db.models.lookups import DateTransform
from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sessions.models import Session
from django.db.models import Q, F, Count, Max, Value
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.template import loader
from .utils import *
from unidecode import unidecode
import pytz
import os
import locale
import json
from datetime import timedelta, datetime
from channels import Channel, Group as ChannelGroup


def common_attributes():
    return [{'html_name': ca.replace('_', '-'), 'description': Property.common_attributes_filed_map[ca]['description'],
             'format': Property.common_attributes_filed_map[ca]['format']}
            for ca in
            sorted(Property.common_attributes_filed_map.keys(),
                   key=lambda ca: ['expenses', 'rooms', 'bathrooms', 'surface', 'covered_surface', 'orientation', 'age',
                                   'garages'].index(ca))]


# Timezone management
# TODO - find a configurable TZ by user (defaulting to their local)
def utc_to_local(utc_dt, tz='America/Argentina/Buenos_Aires'):
    local_tz = pytz.timezone(tz)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)
# Timezone management


# Number format management
def format_number(number, locale_value='es_ES.UTF-8', format_string='%.2f'):
    if number is None:
        return None
    os.environ['LANG'] = locale_value
    locale.setlocale(locale.LC_ALL, '')
    return locale.format(format_string, number, True)
# Number format management


# Time aux calculation
def time_ago(time):
    now = utc_to_local(datetime.utcnow())
    timestamp = utc_to_local(time)
    if now.date() == timestamp.date():
        ago = now - timestamp
        if ago.seconds / 3600 < 1:
            if ago.seconds / 60 < 1:
                return '{0}s'.format(ago.seconds)
            else:
                return '{0}m'.format(ago.seconds // 60)
        else:
            return '{0}h'.format(ago.seconds // 3600)
    else:
        ago = now.date() - timestamp.date()
        return '{0}d'.format(ago.days) if ago.days > 1 else 'Ayer'
# Time aux calculation


class Country(models.Model):
    name = models.CharField(u'País', max_length=100)

    def __unicode__(self):
        return self.name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'full_name': self.name
        }


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(u'Provincia/Estado', max_length=100)

    def __unicode__(self):
        return self.name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country_id': self.country_id,
            'country': self.country.name,
            'full_name': u'{0}, {1}'.format(self.name, self.country.name)
        }


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField('Ciudad', max_length=100)

    def __unicode__(self):
        return self.name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country_id': self.state.country_id,
            'country': self.state.country.name,
            'state_id': self.state_id,
            'state': self.state.name,
            'full_name': u'{0}, {1}, {2}'.format(self.name, self.state.name, self.state.country.name)
        }


class Neighborhood(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField('Barrio/Zona', max_length=100)

    def __unicode__(self):
        return self.name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country_id': self.city.state.country_id,
            'country': self.city.state.country.name,
            'state_id': self.city.state_id,
            'state': self.city.state.name,
            'city_id': self.city_id,
            'city': self.city.name,
            'full_name': u'{0}, {1}, {2}, {3}'.format(self.name, self.city.name, self.city.state.name,
                                                      self.city.state.country.name)
        }


class CompanyPrivacyConfig(models.Model):
    name = models.CharField(u'Nombre', default=u'', unique=True, max_length=50)
    description = models.CharField(u'Descripción', null=True, blank=True, max_length=100)
    order_index = models.IntegerField(u'Orden', null=True, blank=True)

    all_name = u'Todo'
    branch_name = u'Sucursal'
    none_name = u'Nada'

    def __unicode__(self):
        return u'{0} - {1}'.format(self.name, self.description)

    @classmethod
    def all(cls):
        return cls.objects.filter(name=cls.all_name).first()

    @classmethod
    def branch(cls):
        return cls.objects.filter(name=cls.branch_name).first()

    @classmethod
    def none(cls):
        return cls.objects.filter(name=cls.none_name).first()


class Company(models.Model):
    name = models.CharField('Nombre', max_length=50)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    logo_image = models.CharField('Logo', null=True, blank=True, max_length=50)
    privacy_config = models.ForeignKey(CompanyPrivacyConfig, default=CompanyPrivacyConfig.none().id,
                                       on_delete=models.SET_DEFAULT)
    super_agents_can_edit_config = models.BooleanField(u'Super agentes pueden editar configuración', default=False)
    super_agents_can_edit_branches = models.BooleanField(u'Super agentes pueden editar sucursales', default=False)
    super_agents_can_edit_agents = models.BooleanField(u'Super agentes pueden crear/editar/eliminar agentes',
                                                       default=False)
    super_agents_can_config_notifications = models.BooleanField(u'Super agentes pueden configurar notificaciones de '
                                                                u'grupos', default=False)
    super_agents_can_assign_user_to_properties = models.BooleanField(u'Super agentes pueden asignar/desasignar agentes '
                                                                     u'a cargo a propiedades', default=False)
    super_agents_can_assign_user_to_contacts = models.BooleanField(u'Super agentes pueden asignar/desasignar agentes a'
                                                                   u' cargo a contactos', default=False)

    def __unicode__(self):
        return self.name

    @property
    def logo_file_path(self):
        return '{0}{1}/{2}'.format(settings.MEDIA_URL, 'company_logos', self.logo_image)

    def update_logo(self, image):
        try:
            if self.logo_image:  # TODO validate self.logo_file_path exists before attempting remove
                os.remove(self.logo_file_path)
        except (IOError, WindowsError):
            pass
        self.logo_image = '{0}.{1}'.format(self.id, image.name.split('.', 1)[-1:][0])
        with open(self.logo_file_path, 'wb') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

    @property
    def logo_url(self):
        return '/crm/empresa/{0}/logo'.format(self.id)

    @property
    def logo(self):
        try:
            return open(self.logo_file_path, 'rb')
        except IOError:
            self.logo_image = None
            self.save()
            return None

    @property
    def branches(self):
        return sorted(self.branch_set.all(), key=lambda b: b.id)

    @property
    def users(self):
        return User.objects.filter(userextension__company=self)

    def users_with_massive_notifications(self, notification_type=None):
        kwargs = {'is_massive': True}
        if notification_type:
            kwargs['id'] = notification_types[notification_type]
        return [u for u in self.users if [uc for uc in [u.notification_config(None, id=nt.id) for nt in NotificationType
                .objects.filter(**kwargs)] if uc.take_action]]

    @property
    def users_with_automatic_add_in_charge_when_created(self):
        return self.users.filter(userextension__add_new_users_to_my_charge=True)

    @property
    def users_with_automatic_add_in_charge_when_main_branch_set(self):
        return self.users.filter(userextension__add_my_branch_users_to_my_charge=True)

    def created_user(self, user):
        for user_in_charge in self.users_with_automatic_add_in_charge_when_created:
            user_in_charge.add_user_in_charge(user)

    def notify(self, notification_type, related_user, data={}, request=None):
        if settings.NOTIFICATIONS:
            host_url = request.build_absolute_uri('/')[:-1]

            Channel('notify_company').send({
                'company_id': self.id,
                'notification_type': notification_type,
                'related_user_id': related_user.id,
                'data': data,
                'host_url': host_url
            })

    def user_has_access_user(self, user_accessing, user):
        if self.privacy_config == CompanyPrivacyConfig.branch():
            return user_accessing.company == self and user.company == self and user_accessing.main_branch and \
                   user_accessing.main_branch == user.main_branch
        elif self.privacy_config == CompanyPrivacyConfig.none():
            return False

        return True

    def set_user_permissions(self, user):
        if not user.is_admin:
            permissions = [
                (self.super_agents_can_edit_config, Permission.objects.get(codename='edit_config')),
                (self.super_agents_can_edit_branches, Permission.objects.get(codename='edit_branches')),
                (self.super_agents_can_edit_agents, Permission.objects.get(codename='edit_agents')),
                (self.super_agents_can_config_notifications,
                 Permission.objects.get(codename='config_notifications')),
                (self.super_agents_can_assign_user_to_properties,
                 Permission.objects.get(codename='property_assign_agents')),
                (self.super_agents_can_assign_user_to_contacts,
                 Permission.objects.get(codename='contact_assign_agents')),
            ]

            for has_perm, perm in permissions:
                if user.is_super_agent and has_perm:
                    user.user_permissions.add(perm)
                else:
                    user.user_permissions.remove(perm)

            if user.is_super_agent and \
                    (self.super_agents_can_edit_config or self.super_agents_can_edit_branches or
                     self.super_agents_can_edit_agents or self.super_agents_can_config_notifications):
                user.user_permissions.add(Permission.objects.get(codename='view_company_pages'))
            else:
                user.user_permissions.remove(Permission.objects.get(codename='view_company_pages'))

    def set_all_user_permissions(self):
        for user in [u for u in self.users if not u.is_admin]:
            self.set_user_permissions(user)

    @property
    def workflows(self):
        ContactWorkflow.default_workflow(self)
        return self.contactworkflow_set.all()

    @property
    def active_workflow(self):
        return self.workflows.filter(is_active=True).first()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        for group in Group.objects.all():
            for notification_type in notification_types.keys():
                if not GroupNotificationConfig.objects.filter(company=self, group=group,
                                                              notification_type_id=
                                                              notification_types[notification_type]).first():
                    GroupNotificationConfig(company=self, group=group,
                                            notification_type_id=notification_types[notification_type]).save()
        super(Company, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    class Meta:
        permissions = (
            ('view_company_pages', 'Puede ver las pagina de la seccion \'Mi Empresa\''),
            ('edit_config', 'Puede editar la configuracion de la empresa'),
            ('edit_branches', 'Puede editar los datos de las sucursales de la empresa'),
            ('edit_agents', 'Puede editar los usuarios (agentes) de la empresa'),
            ('edit_portals', 'Puede editar la configuracion de portales de la empresa'),
            ('config_notifications', 'Puede editar la configuracion de notificaciones de cada grupo para la empresa'),
            ('edit_workflows', 'Puede editar los workflows de contactos'),
        )


class Branch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    code = models.IntegerField(u'Código', null=True, blank=True)
    name = models.CharField('Nombre', max_length=50)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(u'Dirección', null=True, blank=True, max_length=200)
    description = models.CharField(u'Descripción', null=True, blank=True, max_length=20000)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.code, self.name) if self.code != 0 else self.name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'country': self.city.state.country.name if self.city is not None else '',
            'country_id': self.country_id,
            'state': self.city.state.name if self.city is not None else '',
            'state_id': self.state_id,
            'city': self.city.name if self.city is not None else '',
            'city_id': self.city.id if self.city is not None else '',
            'address': self.address,
            'description': self.description
        }

    @property
    def country_id(self):
        return self.city.state.country.id if self.city else 1

    @property
    def state_id(self):
        return self.city.state.id if self.city else None


class ContactWorkflow(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField('Nombre', max_length=100)
    description = models.CharField(u'Descripción', default='', max_length=4000)
    is_active = models.BooleanField(u'Activo', default=False)
    is_default = models.BooleanField(u'Default', default=False)

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(ContactWorkflow, self).__init__(*args, **kwargs)

    @classmethod
    def default_workflow(cls, company):
        wf = cls.objects.filter(company=company, is_default=True).first()
        if not wf:
            wf = cls(company=company, name='Workflow default', description=u'Descripción del workflow default',
                     is_default=True)
            wf.save()
            pre_contact = ContactWorkflowState(workflow=wf, name=u'Pre-contacto', position='[3, 11]',
                                               color='[153, 153, 0]')
            active_contact = ContactWorkflowState(workflow=wf, name=u'Contacto activo', position='[367, 9]',
                                                  color='[0, 76, 153]')
            inactive_contact = ContactWorkflowState(workflow=wf, name=u'Contacto inactivo', position='[747, 12]',
                                                    color='[0, 0, 0]')
            opportunity = ContactWorkflowState(workflow=wf, name=u'Oportunidad', position='[717, 126]',
                                               color='[0, 153, 0]')
            pending_opportunity = ContactWorkflowState(workflow=wf, name=u'Oportunidad pendiente',
                                                       position='[733, 381]', color='[255, 127, 0]')
            evolving_opportunity = ContactWorkflowState(workflow=wf, name=u'Oportunidad evolucionando',
                                                        position='[32, 361]', color='[76, 153, 0]')
            lost_opportunity = ContactWorkflowState(workflow=wf, name=u'Oportunidad perdida', position='[185, 181]',
                                                    color='[153, 0, 0]')
            realized_opportunity = ContactWorkflowState(workflow=wf, name=u'Oportunidad concretada', position='[2, 78]',
                                                        color='[255, 255, 255]')

            pre_contact.save()
            active_contact.save()
            inactive_contact.save()
            opportunity.save()
            pending_opportunity.save()
            evolving_opportunity.save()
            lost_opportunity.save()
            realized_opportunity.save()

            ContactWorkflowAction(source_state=pre_contact, target_state=active_contact, name=u'Marcar como contacto')\
                .save()
            ContactWorkflowAction(source_state=active_contact, target_state=inactive_contact,
                                  name=u'Marcar como inactivo', automatic_time=90, automatic_unit='d').save()
            ContactWorkflowAction(source_state=inactive_contact, target_state=active_contact,
                                  name=u'Marcar como activo', is_inverse=True).save()
            ContactWorkflowAction(source_state=active_contact, target_state=opportunity,
                                  name=u'Oportunidad identificada').save()
            ContactWorkflowAction(source_state=opportunity, target_state=pending_opportunity,
                                  name=u'Oportunidad pendiete', automatic_time=4, automatic_unit='h').save()
            ContactWorkflowAction(source_state=opportunity, target_state=evolving_opportunity,
                                  name=u'Oportunidad evolucionando').save()
            ContactWorkflowAction(source_state=opportunity, target_state=lost_opportunity, name=u'Oportunidad perdida')\
                .save()
            ContactWorkflowAction(source_state=pending_opportunity, target_state=lost_opportunity,
                                  name=u'Oportunidad perdida', automatic_time=2, automatic_unit='d',
                                  automatic_unlink_agent=True, automatic_notify=True, automatic_email=True).save()
            ContactWorkflowAction(source_state=pending_opportunity, target_state=evolving_opportunity,
                                  name=u'Oportunidad evolucionando').save()
            ContactWorkflowAction(source_state=evolving_opportunity, target_state=lost_opportunity,
                                  name=u'Oportunidad perdida', automatic_time=10, automatic_unit='d',
                                  automatic_notify=True, automatic_email=True, is_inverse=True).save()
            ContactWorkflowAction(source_state=evolving_opportunity, target_state=realized_opportunity,
                                  name=u'Oportunidad concretada').save()
            ContactWorkflowAction(source_state=lost_opportunity, target_state=evolving_opportunity,
                                  name=u'Oportunidad recuperada').save()
            ContactWorkflowAction(source_state=lost_opportunity, target_state=active_contact,
                                  name=u'Oportunidad cerrada', automatic_time=2, automatic_unit='d').save()
            ContactWorkflowAction(source_state=realized_opportunity, target_state=lost_opportunity,
                                  name=u'Oportunidad perdida').save()
            ContactWorkflowAction(source_state=realized_opportunity, target_state=evolving_opportunity,
                                  name=u'Oportunidad no concretada', is_inverse=True).save()
            ContactWorkflowAction(source_state=realized_opportunity, target_state=active_contact,
                                  name=u'Oportunidad cerrada', automatic_time=2, automatic_unit='d').save()

            wf.set_active(only_if_none_is_active=True)
        return wf

    def to_dict(self, workflow_canvas_fields=True):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active' if not workflow_canvas_fields else 'isActive': self.is_active,
            'is_default' if not workflow_canvas_fields else 'isDefault': self.is_default,
            'states': [s.to_dict for s in self.states],
            'actions' if not workflow_canvas_fields else 'links':
                [a.to_dict(include_inverse=True) for a in self.actions if not a.is_inverse]
        }

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not ContactWorkflow.objects.filter(company=self.company, is_active=True).first():
            self.is_active = True
        super(ContactWorkflow, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                          update_fields=update_fields)

    @property
    def actions(self):
        return reduce(lambda actions, state: actions + list(state.actions), self.contactworkflowstate_set.all(), [])

    def set_active(self, only_if_none_is_active=False):
        active_workflows = ContactWorkflow.objects.filter(company=self.company, is_active=True).exclude(id=self.id)
        if not active_workflows or not only_if_none_is_active:
            for workflow in active_workflows:
                workflow.is_active = False
                workflow.save()
            if not self.is_active:
                self.is_active = True
                self.save()

    @property
    def states(self):
        return self.contactworkflowstate_set.all()

    @property
    def has_isolated_states(self):
        return len([s for s in self.states if s.isolated]) > 0

    @property
    def initial_states(self):
        return [s for s in self.states if s.initial_state]

    @property
    def has_no_initial_state(self):
        return len(self.initial_states) == 0

    @property
    def has_many_initial_states(self):
        return len(self.initial_states) > 1

    @property
    def initial_state(self):
        return self.initial_states[0] if not self.has_no_initial_state and not self.has_many_initial_states else None


class ContactWorkflowState(models.Model):
    workflow = models.ForeignKey(ContactWorkflow, on_delete=models.CASCADE)
    name = models.CharField('Nombre', max_length=50)
    position = models.CharField(u'Posición', default='[0, 0]', max_length=50)
    color = models.CharField('Color', default='[0, 0, 0]', max_length=50)

    def __unicode__(self):
        return self.name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.name,
            'position': self.position_array,
            'color': self.color_array
        }

    @property
    def position_array(self):
        return json.loads(self.position)

    @property
    def color_array(self):
        return json.loads(self.color)

    @property
    def background_color_rgb(self):
        return 'rgb({0})'.format(', '.join([str(color) for color in self.color_array]))

    @property
    def font_color(self):
        return '#000000' \
            if int(self.color_array[0] * 299 + self.color_array[1] * 587 + self.color_array[2] * 114) / 1000 > 125 \
            else '#ffffff'

    @property
    def actions(self):
        return ContactWorkflowAction.objects.filter(source_state=self)

    @property
    def isolated(self):
        return len(ContactWorkflowAction.objects.filter(Q(source_state=self) | Q(target_state=self))) == 0

    @property
    def initial_state(self):
        return len(ContactWorkflowAction.objects.filter(target_state=self)) == 0


class ContactWorkflowAction(models.Model):
    source_state = models.ForeignKey(ContactWorkflowState, on_delete=models.CASCADE, related_name='source_state')
    target_state = models.ForeignKey(ContactWorkflowState, on_delete=models.CASCADE, related_name='target_state')
    name = models.CharField('Nombre', max_length=50)
    automatic_time = models.IntegerField('Tiempo', null=True, blank=True)
    automatic_unit = models.CharField('Unidad', null=True, blank=True, max_length=1)
    automatic_unlink_agent = models.BooleanField('Desvincular agente', default=False)
    automatic_notify = models.BooleanField('Notificar', default=False)
    automatic_email = models.BooleanField('Notificar por email', default=False)
    is_inverse = models.BooleanField('Inversa', default=False)

    def __unicode__(self):
        return self.name

    def to_dict(self, include_inverse=False):
        action_dict = {
            'id': self.id,
            'sourceStateId': self.source_state.id,
            'targetStateId': self.target_state.id,
            'text': self.name,
            'automatic': {
                'time': self.automatic_time,
                'unit': self.automatic_unit,
                'unlinkAgent': self.automatic_unlink_agent,
                'notify': self.automatic_notify,
                'email': self.automatic_email
            } if self.automatic_time else None,
        }
        if include_inverse:
            action_dict['inverse'] = self.inverse_action.to_dict() if self.inverse_action else None

        return action_dict

    @property
    def inverse_action(self):
        return ContactWorkflowAction.objects.filter(source_state=self.target_state, target_state=self.source_state)\
            .first()


class ContactPropertyUserCommon(object):
    text_search_relevant_fields = []
    text_search_operation = '__unaccent__icontains'

    def text_search_score(self, search_term):
        return reduce(lambda score, search_word_score: score + search_word_score,
                      [reduce(lambda search_word_score, search_field:
                              search_word_score + ((100 - len(getattr(self, search_field).lower().strip()) +
                                                    len(search_word) * 4) if getattr(self, search_field) and
                                                                             unidecode(search_word).lower() in
                                                                             unidecode(getattr(self, search_field))
                                                   .lower() else 0), self.text_search_relevant_fields, 0)
                       for search_word in search_term.strip().split()], 0)

    @staticmethod
    def string_field_with_matches(string_field, search_term):
        # TODO maintain casing and accents in output. Beware with char '°'
        return reduce(lambda field, search_word:
                      re.compile(unidecode(search_word), re.IGNORECASE).sub('<b>{0}</b>'.format(search_word),
                                                                            unidecode(field)),
                      search_term.strip().split(), string_field)

    def full_name_with_text_search_matches(self, search_term):
        # TODO maintain casing and accents in output. Beware with char '°'
        return self.string_field_with_matches(self.full_name, search_term)

    def email_with_text_search_matches(self, search_term):
        # TODO maintain casing and accents in output. Beware with char '°'
        if self.__class__.__name__ in ['Contact', 'User'] and self.email:
            return self.string_field_with_matches(self.email, search_term)
        return ''


class Contact(models.Model, ContactPropertyUserCommon):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    status = models.ForeignKey(ContactWorkflowState, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField('Nombre', max_length=50)
    last_name = models.CharField('Apellido', null=True, blank=True, max_length=50)
    telephone_number = models.CharField(u'Teléfono', null=True, blank=True, max_length=50)
    email = models.CharField('EMail', null=True, blank=True, max_length=50)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    neighborhood = models.ForeignKey(Neighborhood, null=True, blank=True, on_delete=models.SET_NULL)
    address = models.CharField(u'Dirección', null=True, blank=True, max_length=200)
    document = models.CharField('Documento', null=True, blank=True, max_length=50)
    works_at = models.CharField('Empresa', null=True, blank=True, max_length=50)
    alternative_telephone_number = models.CharField(u'Teléfono alternativo', null=True, blank=True, max_length=50)
    alternative_email = models.CharField('EMail alternativo', null=True, blank=True, max_length=50)
    created = models.DateTimeField('Fecha alta', default=timezone.now)

    # Extra class variables
    text_search_relevant_fields = ['first_name', 'last_name', 'email']
    owner_relationship_type = u'Dueño'
    interested_relationship_type = u'Interesado'

    def __unicode__(self):
        return self.full_name

    @property
    def full_name(self):
        return u'{0}, {1}'.format(self.last_name, self.first_name) if self.last_name else self.first_name

    @property
    def full_name_reversed(self):
        return u'{0} {1}'.format(self.first_name, self.last_name) if self.last_name else self.first_name

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': unicode(self),
            'first_name': self.first_name,
            'last_name': self.last_name,
            'telephone_number': self.telephone_number,
            'email': self.email
        }

    @property
    def url(self):
        return reverse('collaborative_crm:contact', args=('contacto', self.id, ))

    def history(self, last_n_entries=10, starting_entry_number=0, filters={}, user=None):
        return [e for e in self.contactchangelogentry_set.filter(**filters).order_by('-timestamp')
                if e.user_has_permissions(user)][starting_entry_number:last_n_entries]

    def history_count(self, filters={}, user=None):
        return len([e for e in self.contactchangelogentry_set.filter(**filters) if e.user_has_permissions(user)])

    @property
    def last_modified(self):
        return self.contactchangelogentry_set.all().order_by('-timestamp').first()

    def is_related(self, property, rel_type=None):
        filt = {
            'contact': self,
            'parent_property': property
        }
        if rel_type:
            filt['type__description'] = self.owner_relationship_type if rel_type == 'owner'\
                                        else self.interested_relationship_type

        return len(self.contactpropertyrelationship_set.filter(**filt)) > 0

    def is_owner(self, property):
        return self.is_related(property, 'owner')

    def is_interested(self, property):
        return self.is_related(property, 'interested')

    def properties(self, last_n_properties=10, starting_property_number=0, filters={}, user=None):
        q = self.contactpropertyrelationship_set.filter(**filters).order_by('-last_modified_datetime')
        q = [rel for rel in q if not user or user.permissions_over_property(rel.parent_property)] \
            [starting_property_number:last_n_properties]
        return [{'relationship_type': cpr.type.description, 'commentary': cpr.commentary,
                 'last_modified_datetime': cpr.last_modified_datetime, 'parent_property': cpr.parent_property}
                for cpr in q]

    def properties_count(self, user=None):
        return len([rel for rel in self.contactpropertyrelationship_set.all()
                    if not user or user.permissions_over_property(rel.parent_property)])

    def property_data(self, property_id, user=None):
        candidate_properties = self.properties(filters={'parent_property_id': int(property_id)})
        if candidate_properties and (not user or
                                     user.permissions_over_property(candidate_properties[0]['parent_property'])):
            return candidate_properties[0]

        return None

    def searches(self, last_n_searches=10, starting_search_number=0, filters={}):
        return self.contactsearch_set.filter(**filters).order_by('-date')[starting_search_number:last_n_searches]

    @property
    def searches_count(self):
        return self.contactsearch_set.count()

    def search(self, search_id):
        return self.searches(filters={'id': int(search_id)})

    def set_user(self, user, logging_user=None):
        old_user_id = self.user.id if self.user and not user else None
        self.user = user
        self.save()
        if user:
            ContactChangeLogEntry(change_type='contact_user_rel_creation', user=logging_user, contact=self,
                                  new_value=user.id).save()
        else:
            ContactChangeLogEntry(change_type='property_user_rel_destruction', user=logging_user, contact=self,
                                  old_value=old_user_id).save()

    @property
    def get_status(self):
        if not self.status:
            self.set_status(self.company.active_workflow.initial_state)
        return self.status

    def set_status(self, status, logging_user=None):
        if status.workflow == self.company.active_workflow:
            self.status = status
            self.save()
        if logging_user:
            # todo add logging
            pass

    def execute_status_action(self, action, logging_user=None):
        if action in self.get_status.actions:
            self.set_status(action.target_state, logging_user=logging_user)

    class Meta:
        permissions = (
            ('contact_assign_agents', 'Puede asignar agentes a cualquier contacto'),
        )


class ContactSearch(models.Model):
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateTimeField('Fecha', default=timezone.now)
    commentary = models.CharField('Comentarios', null=True, blank=True, max_length=20000)

    def __unicode__(self):
        return u'Búsqueda {0} por {1}'.format(self.id, self.user.full_name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, log_event=None,
             logging_user=None):
        super(ContactSearch, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                        update_fields=update_fields)
        if log_event and logging_user:
            ContactChangeLogEntry(change_type=log_event, user=logging_user, contact=self.contact, attribute=self.id)\
                .save()

    def delete(self, using=None, keep_parents=False, logging_user=None):
        if logging_user:
            ContactChangeLogEntry(change_type='contact_search_removed', user=logging_user, contact=self.contact,
                                  attribute=self.id).save()
        super(ContactSearch, self).delete(using=using, keep_parents=keep_parents)

    def set_commentary(self, new_commentary, logging_user=None):
        old_commentary = self.commentary
        self.commentary = new_commentary
        self.date = datetime.now()
        self.save()
        ContactChangeLogEntry(change_type='contact_search_commentary_edition', user=logging_user, contact=self.contact,
                              attribute=self.id, new_value=self.commentary, old_value=old_commentary).save()

    def to_dict(self, elements_data=False):
        search_dict = {
            'id': self.id,
            'title': unicode(self),
            'user': self.user.to_dict,
            'date': self.date,
            'commentary': self.commentary
        }
        if elements_data:
            search_dict['elements'] = [e.to_dict for e in self.contactsearchelement_set.all()]

        return search_dict

    @property
    def filters(self):
        return reduce(lambda filters, flt: merge_two_dicts(filters, flt.key_value_entry),
                      self.contactsearchelement_set.all(), {'company_id__exact': self.user.company.id})

    @property
    def results(self):
        return Property.objects.filter(**self.filters)


class ContactSearchElement(models.Model):
    search = models.ForeignKey(ContactSearch, on_delete=models.CASCADE)
    attribute = models.CharField('Atributo', max_length=50)
    operation = models.CharField(u'Operación', max_length=50)
    values = models.CharField('Valores', max_length=20000)

    def __unicode__(self):
        return u'Elemento búsqueda {0}, {1}, {2}'.format(self.attribute, self.operation, self.values)

    @property
    def to_dict(self):
        return {
            'attribute': self.attribute,
            'operation': self.operation,
            'values': self.values
        }

    @property
    def decoded_values(self):
        return json.loads(self.values)

    @property
    def unaccent(self):
        return self.decoded_values.__class__ in [str, unicode]

    @property
    def key_value_entry(self):
        return {
            u'{0}__{1}{2}'.format(self.attribute, u'unaccent__' if self.unaccent else '', self.operation):
                self.decoded_values
        }


class ChangeLogEntryType(models.Model):
    description = models.CharField(u'Descripción', max_length=50)
    requires_permissions = models.BooleanField(u'Requiere permisos', default=False)

    def __unicode__(self):
        return self.description


class ChangeLogEntry(object):
    unknown_username = u'Usuario eliminado'
    unknown_property = u'Propiedad eliminada'
    unknown_contact = u'Contacto eliminado'

    creation_description = u'Creación'
    edition_description = u'Edición'
    contact_property_rel_creation_description = u'Relción contacto-propiedad creada'
    contact_property_rel_edition_description = u'Relción contacto-propiedad editada'
    contact_property_rel_destruction_description = u'Relción contacto-propiedad destruida'
    contact_user_rel_creation_description = u'Relción contacto-agente creada'
    contact_user_rel_destruction_description = u'Relción contacto-agente destruida'
    property_user_rel_creation_description = u'Relción propiedad-agente creada'
    property_user_rel_destruction_description = u'Relción propiedad-agente destruida'
    property_attribute_edition_description = u'Edición atributo propiedad'
    property_attribute_creation_description = u'Creación atributo propiedad'
    property_attribute_destruction_description = u'Destrucción atributo propiedad'
    property_image_upload_description = u'Propiedad imagen subida'
    property_image_remove_description = u'Propiedad imagen eliminada'
    property_cover_image_changed_description = u'Propiedad imagen de portada cambiada'
    property_image_description_changed_description = u'Propiedad descripción de imagen cambiada'
    contact_search_creation_description = u'Creación de búsqueda de contacto'
    contact_search_parameters_edition_description = u'Edición de parámetros de búsqueda de contacto'
    contact_search_commentary_edition_description = u'Edición de comentarios de búsqueda de contacto'
    contact_search_removed_description = u'Borrado de búsqueda de contacto'

    attribute_friendly_name_map = {
        'first_name': 'Nombre',
        'last_name': 'Apellido',
        'telephone_number': u'Teléfono',
        'email': 'Email',
        'country': u'País',
        'country_id': u'País',
        'state': 'Provincia/Estado',
        'state_id': 'Provincia/Estado',
        'city': 'Ciudad',
        'city_id': 'Ciudad',
        'neighborhood': 'Barrio/Zona',
        'neighborhood_id': 'Barrio/Zona',
        'address': u'Dirección',
        'document': 'Documento',
        'works_at': 'Empresa',
        'alternative_telephone_number': u'Teléfono alternativo',
        'alternative_email': 'Email alternativo',
        'type': 'Tipo',
        'type_id': 'Tipo',
        'status': 'Estado',
        'status_id': 'Estado',
        'street': 'Calle',
        'number': 'Número',
        'floor': 'Piso',
        'apartment': 'Departamento',
        'intersecting_street_1': 'Entre calle 1',
        'intersecting_street_2': 'Entre calle 2',
        'anonymous_address': u'Dirección ficticia',
        'description': 'Descripción',
        'for_sale': 'En venta',
        'sale_price': 'Precio de venta',
        'sale_price_usd': 'Precio de venta USD',
        'for_rent': 'En alquiler',
        'rent_price': 'Precio de alquiler',
        'rent_price_usd': 'Precio de alquiler USD',
        'expenses': 'Expensas',
        'rooms': 'Ambientes',
        'bathrooms': u'Baños',
        'surface': 'Superficie total',
        'covered_surface': 'Superficie cubierta',
        'orientation': u'Orientación',
        'age': u'Antigüedad',
        'garages': 'Cocheras'
    }

    def custom_constructor(self, *args, **kwargs):
        change_type = kwargs.pop('change_type', None)
        change_types = {
            'creation': self.creation_description,
            'edition': self.edition_description,
            'contact_property_rel_creation': self.contact_property_rel_creation_description,
            'contact_property_rel_edition': self.contact_property_rel_edition_description,
            'contact_property_rel_destruction': self.contact_property_rel_destruction_description,
            'contact_user_rel_creation': self.contact_user_rel_creation_description,
            'contact_user_rel_destruction': self.contact_user_rel_destruction_description,
            'property_user_rel_creation': self.property_user_rel_creation_description,
            'property_user_rel_destruction': self.property_user_rel_destruction_description,
            'property_attribute_edition': self.property_attribute_edition_description,
            'property_attribute_creation': self.property_attribute_creation_description,
            'property_attribute_destruction': self.property_attribute_destruction_description,
            'property_image_upload': self.property_image_upload_description,
            'property_image_remove': self.property_image_remove_description,
            'property_cover_image_changed': self.property_cover_image_changed_description,
            'property_image_description_changed': self.property_image_description_changed_description,
            'contact_search_creation': self.contact_search_creation_description,
            'contact_search_parameters_edition': self.contact_search_parameters_edition_description,
            'contact_search_commentary_edition': self.contact_search_commentary_edition_description,
            'contact_search_removed': self.contact_search_removed_description
        }
        try:
            # if kwargs != {}:
            if change_type:
                kwargs['type_id'] = ChangeLogEntryType.objects.get(description=change_types[change_type]).id
            super(self.__class__, self).__init__(*args, **kwargs)
        except KeyError:
            raise ChangeLogEntry.UnknownChangeType('change_type must be one of {0}'.format(reduce(
                lambda lst, item: lst + '\'{0}\', '.format(item), change_types.keys(), '')[:-2]))

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'html_short_description': self.html_short_description,
            'html_details_title': self.html_details_title,
            'html_details_body': self.html_details_body
        }

    @property
    def permissions_exceptions(self):
        return (self.contact_property_rel_creation or self.contact_property_rel_edition or
                self.contact_property_rel_destruction) and 'owner' not in self.attribute

    @property
    def requires_permissions(self):
        # for contact-property relationships changes, only those related to an owner require permissions
        return self.type.requires_permissions and not self.permissions_exceptions

    def user_has_permissions(self, user):
        return not self.requires_permissions or (user.permissions_over_property(self.get_property) if user else False)

    # TODO - Refactor: move presentation to views
    @property
    def html_short_description(self):
        if self.creation:
            return u'<b>{0}</b> cread{1}'.format(self.main_object, u'o' if self.has_contact else u'a')
        elif self.edition:
            return u'Campo <b>{0}</b> modificado'.format(self.attribute_friendly_name_map[self.attribute])
        elif self.property_user_rel_creation or self.contact_user_rel_creation:
            return u'Agente <b>{0}</b> asignado a cargo'.format(self.get_related_user.full_name
                                                                if self.get_related_user else self.unknown_username)
        elif self.property_user_rel_destruction or self.contact_user_rel_destruction:
            return u'Agente <b>{0}</b> quitado del cargo'.format(self.get_related_user.full_name
                                                                 if self.get_related_user else self.unknown_username)
        elif self.property_attribute_creation:
            return u'Característica <b>{0}</b> creada'.format(self.attribute)
        elif self.property_attribute_edition:
            return u'Característica <b>{0}</b> modificada'.format(self.attribute_friendly_name_map[self.attribute]
                                                                  if self.attribute
                                                                  in self.attribute_friendly_name_map.keys()
                                                                  else self.attribute)
        elif self.property_attribute_destruction:
            return u'Característica <b>{0}</b> eliminada'.format(self.attribute)
        elif self.property_image_upload:
            return u'<b>Imagen</b> subida'
        elif self.property_image_remove:
            return u'<b>Imagen</b> eliminada'
        elif self.property_cover_image_changed:
            return u'<b>Imagen de portada</b> cambiada'
        elif self.property_image_description_changed:
            return u'Descripcion de Imagen <b>\'{0}\'</b> cambiada'.format(self.new_value)
        elif self.contact_search_creation:
            return u'Búsqueda <b>{0}</b> creada'.format(self.attribute)
        elif self.contact_search_parameters_edition:
            return u'Parámetros de búsqueda <b>{0}</b> modificada'.format(self.attribute)
        elif self.contact_search_commentary_edition:
            return u'Comentarios de búsqueda <b>{0}</b> modificados'.format(self.attribute)
        elif self.contact_search_removed:
            return u'Búsqueda <b>{0}</b> eliminada'.format(self.attribute)

        return 'Cambio desconocido - {0} por {1}'.format(self.timestamp, self.username)

    @property
    def html_details_title(self):
        if self.contact_property_rel_creation:
            return u'Creación de vínculo de {0} por {1}'.format(
                u'dueño' if self.attribute == 'owner' else u'interesado', self.user_full_name)
        elif self.contact_property_rel_edition:
            return u'Edición de vínculo de {0} por {1}'.format(
                u'dueño' if self.attribute == 'owner' else u'interesado', self.user_full_name)
        elif self.contact_property_rel_destruction:
            return u'Destrucción de vínculo de {0} por {1}'.format(
                u'dueño' if self.attribute == 'owner' else u'interesado', self.user_full_name)
        elif self.contact_user_rel_creation or self.property_user_rel_creation:
            return u'Agente {0} asignado a cargo por {1}'.format(self.get_related_user.full_name
                                                                if self.get_related_user else self.unknown_username,
                                                                self.user_full_name)
        elif self.contact_user_rel_destruction or self.property_user_rel_destruction:
            return u'Agente {0} quitado del cargo por {1}'.format(self.get_related_user.full_name
                                                                   if self.get_related_user
                                                                   else self.unknown_username, self.user_full_name)
        elif self.property_attribute_creation:
            return u'Creación de característica de {0} por {1}'.format(self.attribute, self.user_full_name)
        elif self.property_attribute_edition:
            return u'Edición de característica {0} por {1}'.format(self.attribute, self.user_full_name)
        elif self.property_attribute_destruction:
            return u'Eliminación de característica de {0} por {1}'.format(self.attribute, self.user_full_name)
        elif self.property_image_upload:
            return u'Imagen subida por {0}'.format(self.user_full_name)
        elif self.property_image_remove:
            return u'Imagen eliminada por {0}'.format(self.user_full_name)
        elif self.property_cover_image_changed:
            return u'Imagen de portada cambiada por {0}'.format(self.user_full_name)
        elif self.property_image_description_changed:
            return u'Descripcion de imagen editada  por {0}'.format(self.user_full_name)
        elif self.contact_search_creation:
            return u'Creación de búsqueda por {0}'.format(self.user_full_name)
        elif self.contact_search_parameters_edition:
            return u'Edición de parámetros de búsqueda por {0}'.format(self.user_full_name)
        elif self.contact_search_commentary_edition:
            return u'Edición de comentarios de búsqueda por {0}'.format(self.user_full_name)
        elif self.contact_search_removed:
            return u'Borrado de búsqueda por {0}'.format(self.user_full_name)

        return 'Cambio desconocido - {0} por {1}'.format(self.timestamp, self.username)

    @property
    def html_details_body(self):
        body = '{0}:<br><br><b>Usuario: </b>{1}<br><b>Fecha y Hora: </b>{2}'.format(
            self.html_short_description, self.username, utc_to_local(self.timestamp).strftime('%d/%m/%Y %H:%M:%S'))

        if self.edition or self.contact_property_rel_edition or self.property_attribute_edition or \
                self.property_image_description_changed or self.contact_search_commentary_edition:
            body += u'<br><b>Nuevo valor: </b>{0}<br><b>Viejo valor: </b>{1}'.format(self.decoded_new_value,
                                                                                     self.decoded_old_value)
        if self.property_user_rel_creation or self.contact_user_rel_creation or self.property_user_rel_destruction or\
                self.contact_user_rel_destruction:
            body += u'<br><b>Usuario afectado: </b>{0}'.format(self.get_related_user.username if self.get_related_user
                                                               else self.unknown_username)
        if self.property_image_upload:
            body += u'<br><b>Imagen: </b><a href="{0}" target="_blank">Ver</a>'.format(self.get_new_image.image_url) \
                if self.get_new_image else u'<br><b>Imagen: </b> Eliminada'

        if self.property_image_description_changed:
            body += u'<br><b>Imagen: </b><a href="{0}" target="_blank">Ver</a>'.format(self.decoded_attribute) \
                if self.decoded_attribute != self.attribute else u'<br><b>Imagen: </b> Eliminada'

        if self.property_image_remove:
            body += u'<br><b>Descripción: </b>{0}'.format(self.old_value if self.old_value else u'-')

        if self.property_cover_image_changed:
            body += u'<br><b>Nueva portada: </b><a href="{0}" target="_blank">Ver</a>'.format(
                self.get_new_image.image_url) if self.get_new_image else u'<br><b>Nueva portada: </b> Eliminada'
            body += u'<br><b>Nueva portada: </b><a href="{0}" target="_blank">Ver</a>'.format(
                self.get_old_image.image_url) if self.get_old_image else u'<br><b>Vieja portada: </b> {0}'\
                .format('Eliminada' if self.get_old_image is not None else '-')

        if self.contact_search_creation or self.contact_search_parameters_edition or \
                self.contact_search_commentary_edition or self.contact_search_removed:
            body += u'<br><b>Búsqueda: </b>{0}'.format(self.attribute)

        return body
    # TODO - Refactor: move presentation to views

    @property
    def main_object(self):
        if self.__class__ == ContactChangeLogEntry:
            return self.contact
        elif self.__class__ == PropertyChangeLogEntry:
            return self.parent_property
        return None

    @property
    def get_contact(self):
        if self.has_contact:
            if self.__class__ == ContactChangeLogEntry:
                return self.contact
            elif self.contact_property_rel_edition:
                return Contact.objects.filter(id=int(self.attribute.split('-', 1)[0])).first()
            else:
                try:
                    return Contact.objects.get(id=int(self.new_value if self.new_value else
                                                      (self.old_value if self.old_value else 0)))
                except Contact.DoesNotExist:
                    return self.unknown_contact
        return None

    @property
    def get_property(self):
        if self.has_property:
            if self.__class__ == PropertyChangeLogEntry:
                return self.parent_property
            elif self.contact_property_rel_edition:
                return Property.objects.filter(id=int(self.attribute.split('-', 1)[0])).first()
            else:
                try:
                    return Property.objects.get(id=int(self.new_value if self.new_value else
                                                       (self.old_value if self.old_value else 0)))
                except Property.DoesNotExist:
                    return self.unknown_property
        return None

    @property
    def get_related_user(self):
        if self.has_user:
            try:
                return User.objects.get(id=int(self.new_value if self.new_value else
                                               (self.old_value if self.old_value else 0)))
            except User.DoesNotExist:
                pass
        return None

    @property
    def get_new_image(self):
        if self.has_image and self.new_value:
            try:
                return PropertyImage.objects.get(id=int(self.new_value))
            except PropertyImage.DoesNotExist:
                pass

        return None

    @property
    def get_old_image(self):
        if self.has_image and self.old_value:
            try:
                return PropertyImage.objects.get(id=int(self.old_value))
            except PropertyImage.DoesNotExist:
                return 0

        return None

    def decode_value(self, value):
        if value and self.proxy_class and self.proxy_source_field and self.proxy_target_field:
            try:
                return eval('{0}.objects.get({1}=\'{2}\').{3}'.format(self.proxy_class, self.proxy_source_field, value,
                                                                      self.proxy_target_field))
            except Exception:
                pass

        return value if value else u'-'

    @property
    def decoded_new_value(self):
        return self.decode_value(self.new_value)

    @property
    def decoded_old_value(self):
        return self.decode_value(self.old_value)

    @property
    def decoded_attribute(self):
        return self.decode_value(self.attribute)

    @property
    def username(self):
        return self.user.username if self.user is not None else self.unknown_username

    @property
    def user_full_name(self):
        return self.user.full_name if self.user is not None else self.unknown_username

    @property
    def creation(self):
        return self.type.description == self.creation_description

    @property
    def edition(self):
        return self.type.description == self.edition_description

    @property
    def contact_property_rel_creation(self):
        return self.type.description == self.contact_property_rel_creation_description

    @property
    def contact_property_rel_edition(self):
        return self.type.description == self.contact_property_rel_edition_description

    @property
    def contact_property_rel_destruction(self):
        return self.type.description == self.contact_property_rel_destruction_description

    @property
    def contact_user_rel_creation(self):
        return self.type.description == self.contact_user_rel_creation_description

    @property
    def contact_user_rel_destruction(self):
        return self.type.description == self.contact_user_rel_destruction_description

    @property
    def property_user_rel_creation(self):
        return self.type.description == self.property_user_rel_creation_description

    @property
    def property_user_rel_destruction(self):
        return self.type.description == self.property_user_rel_destruction_description

    @property
    def property_attribute_edition(self):
        return self.type.description == self.property_attribute_edition_description

    @property
    def property_attribute_creation(self):
        return self.type.description == self.property_attribute_creation_description

    @property
    def property_attribute_destruction(self):
        return self.type.description == self.property_attribute_destruction_description

    @property
    def property_image_upload(self):
        return self.type.description == self.property_image_upload_description

    @property
    def property_image_remove(self):
        return self.type.description == self.property_image_remove_description

    @property
    def property_cover_image_changed(self):
        return self.type.description == self.property_cover_image_changed_description

    @property
    def property_image_description_changed(self):
        return self.type.description == self.property_image_description_changed_description

    @property
    def contact_search_creation(self):
        return self.type.description == self.contact_search_creation_description

    @property
    def contact_search_parameters_edition(self):
        return self.type.description == self.contact_search_parameters_edition_description

    @property
    def contact_search_commentary_edition(self):
        return self.type.description == self.contact_search_commentary_edition_description

    @property
    def contact_search_removed(self):
        return self.type.description == self.contact_search_removed_description

    @property
    def has_contact(self):
        return self.__class__ == ContactChangeLogEntry or self.contact_property_rel_creation or \
               self.contact_property_rel_edition or self.contact_property_rel_destruction

    @property
    def has_property(self):
        return self.__class__ == PropertyChangeLogEntry or self.contact_property_rel_creation or \
               self.contact_property_rel_edition or self.contact_property_rel_destruction

    @property
    def has_user(self):
        return self.property_user_rel_creation or self.property_user_rel_destruction or self.contact_user_rel_creation \
               or self.contact_user_rel_destruction

    @property
    def has_image(self):
        return self.property_image_upload or self.property_cover_image_changed

    @property
    def type_description(self):
        return self.type.description if self.type else u'Desconocido'

    @property
    def attribute_user_friendly_name(self):
        try:
            return self.attribute_friendly_name_map[self.attribute]
        except KeyError:
            return self.attribute

    class UnknownChangeType(ValueError):

        def __init__(self, *args, **kwargs):
            super(ChangeLogEntry.UnknownChangeType, self).__init__(*args, **kwargs)


class ContactChangeLogEntry(models.Model, ChangeLogEntry):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('Timestamp', default=timezone.now)
    type = models.ForeignKey(ChangeLogEntryType, null=True, blank=True, on_delete=models.SET_NULL)
    attribute = models.CharField('Atributo', max_length=50)
    old_value = models.CharField('Viejo valor', null=True, blank=True, max_length=4000)
    new_value = models.CharField('Nuevo valor', null=True, blank=True, max_length=4000)
    proxy_class = models.CharField('Clase intermediaria', null=True, blank=True, max_length=50)
    proxy_source_field = models.CharField('Campo origen de clase intermediaria', null=True, blank=True, max_length=50)
    proxy_target_field = models.CharField('Campo destino de clase intermediaria', null=True, blank=True, max_length=50)

    def __init__(self, *args, **kwargs):
        self.custom_constructor(*args, **kwargs)

    @property
    def html_short_description(self):
        if self.contact_property_rel_creation:
            return u'Vinculado como <b>{0}</b> de <b>{1}</b>'.format(u'dueño' if self.attribute == 'owner'
                                                                     else u'interesado', self.get_property)
        elif self.contact_property_rel_edition:
            property = self.get_property
            return u'Comentarios editados de vínculo con <b>{0} ({1})</b>'.format(property if property else
                                                                                  self.unknown_property, u'dueño'
                                                                                  if self.attribute.split('-', 1)[1]
                                                                                     == 'owner' else u'interesado')
        elif self.contact_property_rel_destruction:
            return u'<u>Des</u>vinculado como <b>{0}</b> de <b>{1}</b>'.format(u'dueño' if self.attribute == 'owner'
                                                                               else u'interesado', self.get_property)

        return super(ContactChangeLogEntry, self).html_short_description

    @property
    def html_details_title(self):
        if self.creation:
            return u'Creación del contacto {0} por {1}'.format(self.contact, self.user_full_name)
        if self.edition:
            return u'Edición de campo {0} del contacto por {1}'.format(self.attribute_friendly_name_map[self.attribute],
                                                                       self.user_full_name)
        if self.contact_property_rel_edition:
            return u'Edición de comentarios de relación con propiedad por {0}'.format(self.user_full_name)

        return super(ContactChangeLogEntry, self).html_details_title


class PropertyStatus(models.Model):
    name = models.CharField('Nombre', max_length=50)
    description = models.CharField(u'Descripción', default='', max_length=100)

    def __unicode__(self):
        return self.name


class PropertyType(models.Model):
    description = models.CharField(u'Descripción', max_length=50)

    def __unicode__(self):
        return self.description


class Property(models.Model, ContactPropertyUserCommon):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    contacts = models.ManyToManyField(Contact, through='ContactPropertyRelationship')

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    type = models.ForeignKey(PropertyType, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.ForeignKey(PropertyStatus, null=True, blank=True, on_delete=models.SET_NULL)

    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    neighborhood = models.ForeignKey(Neighborhood, null=True, blank=True, on_delete=models.SET_NULL)
    street = models.CharField('Calle', max_length=50)
    number = models.CharField(u'Número', null=True, blank=True, max_length=50)
    floor = models.CharField('Piso', null=True, blank=True, max_length=50)
    apartment = models.CharField('Departamento', null=True, blank=True, max_length=50)
    intersecting_street_1 = models.CharField('Entre calles 1', null=True, blank=True, max_length=50)
    intersecting_street_2 = models.CharField('Entre calles 2', null=True, blank=True, max_length=50)
    anonymous_address = models.CharField(u'Dirección ficticia', null=True, blank=True, max_length=50)
    description = models.CharField(u'Descripción', default='', max_length=20000)

    for_sale = models.BooleanField('En venta', default=False)
    sale_price = models.IntegerField('Precio venta', null=True, blank=True)
    sale_price_usd = models.IntegerField('Precio venta USD', null=True, blank=True)
    for_rent = models.BooleanField('En alquiler', default=False)
    rent_price = models.IntegerField('Precio alquiler', null=True, blank=True)
    rent_price_usd = models.IntegerField('Precio alquiler USD', null=True, blank=True)

    expenses = models.IntegerField('Expensas', null=True, blank=True)
    rooms = models.IntegerField('Ambientes', null=True, blank=True)
    bathrooms = models.IntegerField(u'Baños', null=True, blank=True)
    surface = models.IntegerField('Superficie total', null=True, blank=True)
    covered_surface = models.IntegerField('Superficie cubierta', null=True, blank=True)
    orientation = models.CharField(u'Orientación', null=True, blank=True, max_length=100)
    age = models.IntegerField(u'Antigüedad', null=True, blank=True)
    garages = models.IntegerField(u'Cocheras', null=True, blank=True)

    # Extra class variables
    pending_appraisal_status_name = u'Pendiente de tasación'
    unavailable_status_name = u'No disponible'
    available_status_name = u'Disponible'
    default_status_name = pending_appraisal_status_name
    default_country_name = u'Argentina'
    owner_relationship_type = u'Dueño'
    interested_relationship_type = u'Interesado'
    common_attributes_filed_map = {
        'expenses': {'description': 'Expensas', 'unit': {'type': 'prefix', 'value': '$'}, 'format': u'Número',
                     'image': 'expenses.png'},
        'rooms': {'description': 'Ambientes', 'unit': None, 'format': u'Número', 'image': 'rooms.png'},
        'bathrooms': {'description': u'Baños', 'unit': None, 'format': u'Número', 'image': 'bathrooms.png'},
        'surface': {'description': 'Superficie total', 'unit': {'type': 'suffix', 'value': u'm²'},
                    'format': u'Número', 'image': 'surface.png'},
        'covered_surface': {'description': 'Superficie cubierta', 'unit': {'type': 'suffix', 'value': u'm²'},
                            'format': u'Número', 'image': 'covered_surface.png'},
        'orientation': {'description': u'Orientación', 'unit': None, 'format': None, 'image': 'orientation.png'},
        'age': {'description': u'Antigüedad', 'unit': {'type': 'suffix', 'value': u'Años'}, 'format': u'Número',
                'image': 'age.png'},
        'garages': {'description': 'Cocheras', 'unit': None, 'format': u'Número', 'image': 'garages.png'}
    }
    text_search_relevant_fields = ['street', 'number', 'floor', 'apartment']

    def __unicode__(self):
        return self.full_name

    @property
    def full_name(self):
        return (self.street + ((' ' + self.number) if self.number is not None else '') +
                (' ' if self.floor is not None or self.apartment is not None else '') +
                ((self.floor + ('°' if re.search('^([0-9]+)$', self.floor) is not None else '') + ' ')
                 if self.floor is not None else '') + (self.apartment if self.apartment is not None else '')).strip()

    @property
    def url(self):
        return reverse('collaborative_crm:property', args=(self.id, ))

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'name': unicode(self),
            'url': self.url,
            'type': self.type.description if self.type is not None else '',
            'status': self.status.name if self.status is not None else '',
            'country': self.city.state.country.name if self.city is not None else '',
            'country_id': self.city.state.country.id if self.city is not None else '',
            'state': self.city.state.name if self.city is not None else '',
            'state_id': self.city.state.id if self.city is not None else '',
            'city': self.city.name if self.city is not None else '',
            'city_id': self.city.id if self.city is not None else '',
            'neighborhood': self.neighborhood.name if self.neighborhood is not None else '',
            'neighborhood_id': self.neighborhood.id if self.neighborhood is not None else '',
            'street': self.street,
            'number': self.number,
            'floor': self.floor,
            'apartment': self.apartment,
            'intersecting_street_1': self.intersecting_street_1,
            'intersecting_street_2': self.intersecting_street_2,
            'anonymous_address': self.anonymous_address,
            'description': self.description,
            'for_sale': self.for_sale,
            'sale_price': format_number(self.sale_price),
            'sale_price_usd': format_number(self.sale_price_usd),
            'for_rent': self.for_rent,
            'rent_price': format_number(self.rent_price),
            'rent_price_usd': format_number(self.rent_price_usd),
            'extra_attributes': self.extra_attributes,
            'cover_image_url': self.cover_image.image_url if self.cover_image else None,
            'images_details': [{'image_url': i.image_url, 'description': i.description} for i in self.images]
        }

    @property
    def generate_anonymous_address(self):
        return self.street + ((' ' + ((self.number.replace(' ', '')[:-2] + '00') if int(self.number) >= 100 else '1'))
                              if self.number is not None and re.match(r'^[0-9| ]+$', self.number) is not None else '')

    @property
    def status_id_value(self):
        return self.status.id if self.status else PropertyStatus.objects.get(name=self.default_status_name).id

    @property
    def pending_appraisal(self):
        return (self.sale_price is None or self.sale_price == 0) and (self.rent_price is None or self.rent_price == 0)\
               and (self.sale_price_usd is None or self.sale_price_usd == 0) and\
               (self.rent_price_usd is None or self.rent_price_usd == 0)

    @property
    def unavailable(self):
        return not self.for_sale and not self.for_rent

    def check_status_consistency(self):
        # Status is locked if property is either unavailable (neither for sale/rent) or pending appraisal info
        if (self.unavailable or self.pending_appraisal) and \
                (self.status not in PropertyStatus.objects.filter(name__in=[self.unavailable_status_name,
                                                                            self.pending_appraisal_status_name])):
            raise Property.PropertyStatusInconsistent()

    @property
    def country_id(self):
        return self.city.state.country.id if self.city is not None else \
            Country.objects.get(name=self.default_country_name).id

    @property
    def state_id(self):
        return self.city.state.id if self.city is not None else 0

    @property
    def city_id_value(self):
        return self.city.id if self.city is not None else 0

    def history(self, last_n_entries=10, starting_entry_number=0, filters={}, user=None):
        return [e for e in self.propertychangelogentry_set.filter(**filters).order_by('-timestamp')
                if e.user_has_permissions(user)][starting_entry_number:last_n_entries]

    def history_count(self, filters={}, user=None):
        return len([e for e in self.propertychangelogentry_set.filter(**filters) if e.user_has_permissions(user)])

    @property
    def last_modified(self):
        return self.propertychangelogentry_set.all().order_by('-timestamp').first()

    @property
    def owner(self):
        query = self.contactpropertyrelationship_set\
            .filter(type=ContactPropertyRelationshipType.objects.get(description=self.owner_relationship_type))
        return query[0] if len(query) > 0 else None

    def interested_contacts(self, last_n_contacts=10, starting_contact_number=0, filters={}):
        filters['type'] = ContactPropertyRelationshipType.objects.get(description=self.interested_relationship_type)
        q = self.contactpropertyrelationship_set.filter(**filters)\
                .order_by('-last_modified_datetime')[starting_contact_number:last_n_contacts]
        return [{'commentary': cpr.commentary, 'last_modified_datetime': cpr.last_modified_datetime,
                 'contact': cpr.contact} for cpr in q]

    @staticmethod
    def format_value(value, unit, unit_prefix):
        return u'{0}{1}{2}'.format(u'{0} '.format(unit) if unit and unit_prefix else '', value,
                                   u' {0}'.format(unit) if unit and not unit_prefix else '') if value else None

    @property
    def extra_attributes(self):
        return [{
                   'description': self.common_attributes_filed_map[f]['description'],
                   'value': getattr(self, f), 'unit': self.common_attributes_filed_map[f]['unit'],
                   'format': self.common_attributes_filed_map[f]['format'],
                   'image': self.common_attributes_filed_map[f]['image'], 'type': 'common', 'field_name': f,
                   'formatted_value': self.format_value(getattr(self, f),
                                                        self.common_attributes_filed_map[f]['unit']['value']
                                                        if self.common_attributes_filed_map[f]['unit'] else None,
                                                        self.common_attributes_filed_map[f]['unit']['type'] == 'prefix'
                                                        if self.common_attributes_filed_map[f]['unit'] else None)
               } for f in ['expenses', 'rooms', 'bathrooms', 'surface', 'covered_surface', 'orientation', 'age',
                           'garages']] +\
                [{'description': ea.description, 'value': ea.value, 'unit': ea.unit_dict, 'format': ea.format,
                  'image': 'info.png', 'type': 'custom', 'field_name': ea.description,
                  'formatted_value': ea.formatted_value} for ea in self.propertyextraattribute_set.all()]

    @property
    def has_extra_attributes(self):
        return len([ea for ea in self.extra_attributes if ea['type'] == 'custom' or ea['value']]) > 0

    @property
    def attributes_string(self):
        return reduce(lambda attr_string, attr: attr_string + (u' | ' + attr) if attr else u'',
                      [
                          '{0} m<sup>2</sup>'.format(self.surface) if self.surface else None,
                          '{0} AMBIENTE{1}'.format(self.rooms, u'S' if self.rooms > 1 else u'') if self.rooms else None,
                          '{0} COCHERA{1}'.format(self.garages, u'S' if self.garages > 1 else u'') if self.garages
                          else None
                      ], u'')[3:]

    @property
    def cover_image(self):
        return self.propertyimage_set.filter(cover_image=True)[0] \
            if self.propertyimage_set.filter(cover_image=True) else (self.propertyimage_set.all().order_by('id')[0]
                                                                     if self.propertyimage_set.all() else None)

    @property
    def images(self):
        return sorted(self.propertyimage_set.all(), key=lambda i: i.id)

    def set_cover_image(self, image, logging_user=None):
        current_cover_images = self.propertyimage_set.select_for_update().filter(cover_image=True)
        old_cover_image_id = None
        if current_cover_images:
            old_cover_image_id = current_cover_images[0].id
            current_cover_images[0].cover_image = False
            current_cover_images[0].save()
        image.cover_image = True
        image.save()
        if logging_user:
            PropertyChangeLogEntry(change_type='property_cover_image_changed', user=logging_user, parent_property=self,
                                   new_value=image.id, old_value=old_cover_image_id).save()

    def set_user(self, user, logging_user=None):
        old_user_id = self.user.id if self.user and not user else None
        self.user = user
        self.save()
        if user:
            PropertyChangeLogEntry(change_type='property_user_rel_creation', user=logging_user, parent_property=self,
                                   new_value=user.id).save()
        else:
            PropertyChangeLogEntry(change_type='property_user_rel_destruction', user=logging_user, parent_property=self,
                                   old_value=old_user_id).save()

    def get_file(self, file_type='excel', hide_exact_address=False, include_images=True, include_cover_image=True):
        title = self.anonymous_address if self.anonymous_address else u'{0} {1}'.format(self.street, self.number)

        cover_image_url = ''
        cover_image_offset = 0
        if include_cover_image and self.cover_image:
            cover_image_url = self.cover_image.image_path
            cover_image_offset = 4

        images = None
        if include_images:
            images = {
                'col': 2,
                'start_at_row': 16,
                'images': self.images
            }

        values = [
            {'value': '', 'row': 1, 'col': 1, 'format': 'col-width-3'},
            {'value': '', 'row': 1, 'col': 6 + cover_image_offset, 'format': 'col-width-3'},
            {'value': '', 'row': 1, 'col': 9 + cover_image_offset, 'format': 'col-width-3'},

            {'value': title, 'row': 1, 'col': [2, 11 + cover_image_offset], 'format': 'bold font-size-14'},

            {'value': 'Tipo', 'row': 3, 'col': [c + cover_image_offset for c in [2, 3]],
             'format': 'bold border-left-thick border-top-thick', 'table': 'table-1'},
            {'value': self.type.description, 'row': 4, 'col': [c + cover_image_offset for c in [2, 3]],
             'format': 'border-left-thick', 'table': 'table-1'},
            {'value': 'Estado', 'row': 3, 'col': [c + cover_image_offset for c in [4, 5]],
             'format': 'bold border-right-thick border-top-thick', 'table': 'table-1'},
            {'value': self.status.name, 'row': 4, 'col': [c + cover_image_offset for c in [4, 5]],
             'format': 'border-right-thick', 'table': 'table-1'},

            {'value': '', 'row': 5, 'col': [c + cover_image_offset for c in [2, 5]],
             'format': 'border-left-thick border-right-thick', 'table': 'table-1'},

            {'value': u'País', 'row': 6, 'col': 2 + cover_image_offset, 'format': 'bold border-left-thick col-width-15',
             'table': 'table-1'},
            {'value': self.city.state.country.name, 'row': 7, 'col': 2 + cover_image_offset,
             'format': 'border-left-thick{0}'.format('border-bottom-thick' if hide_exact_address else ''),
             'table': 'table-1'},
            {'value': 'Provincia / Estado', 'row': 6, 'col': 3 + cover_image_offset, 'format': 'bold col-width-15',
             'table': 'table-1'},
            {'value': self.city.state.name, 'row': 7, 'col': 3 + cover_image_offset,
             'format': 'border-bottom-thick' if hide_exact_address else '', 'table': 'table-1'},
            {'value': 'Ciudad', 'row': 6, 'col': 4 + cover_image_offset, 'format': 'bold col-width-15',
             'table': 'table-1'},
            {'value': self.city.name, 'row': 7, 'col': 4 + cover_image_offset,
             'format': 'border-bottom-thick' if hide_exact_address else '', 'table': 'table-1'},
            {'value': 'Barrio / Zona', 'row': 6, 'col': 5 + cover_image_offset,
             'format': 'bold border-right-thick col-width-15', 'table': 'table-1'},
            {'value': self.neighborhood.name if self.neighborhood else '-', 'row': 7, 'col': 5 + cover_image_offset,
             'format': 'border-right-thick{0}'.format(' border-bottom-thick' if hide_exact_address else ''),
             'table': 'table-1'},

            {'value': '', 'condition': not hide_exact_address, 'row': 8, 'col': [c + cover_image_offset for c in [2, 5]],
             'format': 'border-left-thick border-right-thick', 'table': 'table-1'},

            {'value': 'Calle', 'condition': not hide_exact_address, 'row': 9, 'col': 2 + cover_image_offset,
             'format': 'bold border-left-thick', 'table': 'table-1'},
            {'value': self.street, 'condition': not hide_exact_address, 'row': 10, 'col': 2 + cover_image_offset,
             'format': 'border-left-thick', 'table': 'table-1'},
            {'value': u'Número', 'condition': not hide_exact_address, 'row': 9, 'col': 3 + cover_image_offset,
             'format': 'bold', 'table': 'table-1'},
            {'value': self.number, 'condition': not hide_exact_address, 'row': 10, 'col': 3 + cover_image_offset,
             'format': '', 'table': 'table-1'},
            {'value': 'Piso', 'condition': not hide_exact_address, 'row': 9, 'col': 4 + cover_image_offset,
             'format': 'bold', 'table': 'table-1'},
            {'value': self.floor if self.floor else '-', 'condition': not hide_exact_address, 'row': 10,
             'col': 4 + cover_image_offset, 'format': '', 'table': 'table-1'},
            {'value': 'Departamento', 'condition': not hide_exact_address, 'row': 9, 'col': 5 + cover_image_offset,
             'format': 'bold border-right-thick', 'table': 'table-1'},
            {'value': self.apartment if self.apartment else '-', 'condition': not hide_exact_address, 'row': 10,
             'col': 5 + cover_image_offset, 'format': 'border-right-thick', 'table': 'table-1'},

            {'value': '', 'condition': not hide_exact_address, 'row': 11,
             'col': [c + cover_image_offset for c in [2, 5]],
             'format': 'border-left-thick border-right-thick border-bottom-thick', 'table': 'table-1'},

            {'value': u'Descripción', 'row': 13, 'col': [c + cover_image_offset for c in [2, 11]],
             'format': 'bold border-left-thick border-right-thick border-top-thick', 'table': 'table-2'},
            {'value': self.description if self.description else '-', 'row': 14,
             'col': [c + cover_image_offset for c in [2, 11]],
             'format': 'wrap-text row-height-50 border-bottom-thick border-left-thick border-right-thick',
             'table': 'table-2'},

            {'value': 'En venta', 'row': 3, 'col': [c + cover_image_offset for c in [7, 8]],
             'format': 'bold h-center border-left-thick border-right-thick border-top-thick', 'table': 'table-3'},
            {'value': u'Sí' if self.for_sale else 'No', 'row': 4, 'col': [c + cover_image_offset for c in [7, 8]],
             'format': 'h-center border-left-thick border-right-thick', 'table': 'table-3'},
            {'value': '', 'row': 5, 'col': [c + cover_image_offset for c in [7, 8]],
             'format': 'border-left-thick border-right-thick', 'table': 'table-3'},
            {'value': 'ARS', 'row': 6, 'col': 7 + cover_image_offset,
             'format': 'h-center border-left-thick col-width-4', 'table': 'table-3'},
            {'value': self.sale_price if self.sale_price else '-', 'row': 6, 'col': 8 + cover_image_offset,
             'format': '$0 h-center border-right-thick col-width-13', 'table': 'table-3'},
            {'value': 'USD', 'row': 7, 'col': 7 + cover_image_offset,
             'format': 'h-center border-bottom-thick border-left-thick', 'table': 'table-3'},
            {'value': self.sale_price_usd if self.sale_price_usd else '-', 'row': 7, 'col': 8 + cover_image_offset,
             'format': '$0 h-center border-right-thick border-bottom-thick', 'table': 'table-3'},

            {'value': 'En alquiler', 'row': 3, 'col': [c + cover_image_offset for c in [10, 11]],
             'format': 'bold h-center border-left-thick border-right-thick border-top-thick', 'table': 'table-4'},
            {'value': u'Sí' if self.for_rent else 'No', 'row': 4, 'col': [c + cover_image_offset for c in [10, 11]],
             'format': 'h-center border-left-thick border-right-thick', 'table': 'table-4'},
            {'value': '', 'row': 5, 'col': [c + cover_image_offset for c in [10, 11]],
             'format': 'border-left-thick border-right-thick', 'table': 'table-4'},
            {'value': 'ARS', 'row': 6, 'col': 10 + cover_image_offset,
             'format': 'h-center border-left-thick col-width-4', 'table': 'table-4'},
            {'value': self.rent_price if self.rent_price else '-', 'row': 6, 'col': 11 + cover_image_offset,
             'format': '$0 h-center border-right-thick col-width-13', 'table': 'table-4'},
            {'value': 'USD', 'row': 7, 'col': 10 + cover_image_offset,
             'format': 'h-center border-bottom-thick border-left-thick', 'table': 'table-4'},
            {'value': self.rent_price_usd if self.rent_price_usd else '-', 'row': 7, 'col': 11 + cover_image_offset,
             'format': '$0 h-center border-right-thick border-bottom-thick', 'table': 'table-4'},

            {'value': 'Agente a cargo', 'condition': self.user, 'row': 9,
             'col': [c + cover_image_offset for c in [7, 11]],
             'format': 'bold border-left-thick border-right-thick border-top-thick', 'table': 'table-5'},
            {'value': self.user.full_name if self.user else None, 'condition': self.user, 'row': 10,
             'col': [c + cover_image_offset for c in [7, 11]], 'format': 'border-left-thick border-right-thick',
             'table': 'table-5'},
            {'value': self.user.username if self.user else None, 'condition': self.user, 'row': 11,
             'col': [c + cover_image_offset for c in [7, 9]], 'format': 'border-left-thick border-bottom-thick',
             'table': 'table-5'},
            {'value': self.user.telephone_number if self.user and self.user.telephone_number else '-',
             'condition': self.user, 'row': 11, 'col': [c + cover_image_offset for c in [10, 11]],
             'format': 'border-bottom-thick border-right-thick', 'table': 'table-5'},
        ]

        if file_type == 'excel':
            return generate_excel(title, values, cover_image={'cell': 'B3', 'url': cover_image_url}, images=images,
                                  hide_gridlines=True)
        elif file_type == 'pdf':
            return generate_pdf(title, values, cover_image={'cell': 'B3', 'url': cover_image_url}, images=images)

        return ValueError('file_type ahs to be one of \'excel\' or \'pdf')

    class Meta:
        permissions = (
            ('property_assign_agents', 'Puede asignar agentes a cualquier propiedad'),
        )

    class PropertyStatusInconsistent(ValueError):
        def __init__(self, *args, **kwargs):
            super(Property.PropertyStatusInconsistent, self).__init__(*args, **kwargs)


class PropertyExtraAttribute(models.Model):
    related_property = models.ForeignKey(Property, on_delete=models.CASCADE)
    description = models.CharField(u'Descripción', max_length=200)
    value = models.CharField('Valor', default='', max_length=200)
    unit = models.CharField('Unidad', null=True, blank=True, max_length=5)
    unit_prefix = models.BooleanField('Unidad prefijo', default=False)
    format = models.CharField('Formato', null=True, blank=True, max_length=50)

    def __unicode__(self):
        return self.description

    def delete(self, using=None, keep_parents=False, logging_user=None):
        if logging_user:
            PropertyChangeLogEntry(change_type='property_attribute_destruction', user=logging_user,
                                   parent_property=self.related_property,
                                   attribute=self.description).save()
        super(PropertyExtraAttribute, self).delete(using=using, keep_parents=keep_parents)

    @property
    def unit_dict(self):
        return {'type': 'prefix' if self.unit_prefix else 'suffix', 'value': self.unit} if self.unit else None

    @property
    def formatted_value(self):
        return self.related_property.format_value(self.value, self.unit, self.unit_prefix)


class PropertyImage(models.Model):
    parent_property = models.ForeignKey(Property, on_delete=models.CASCADE)
    image_file_name = models.CharField(u'Nombre de archivo de imagen', max_length=50)
    description = models.CharField(u'Descripción', default='', max_length=200)
    cover_image = models.BooleanField(u'Imagen de portada', default=False)

    images_dir = settings.MEDIA_URL + 'properties_images'

    def __init__(self, *args, **kwargs):
        image_file = None
        if 'image' in kwargs:
            image_file = kwargs.pop('image', None)
        logging_user = None
        if 'logging_user' in kwargs:
            logging_user = kwargs.pop('logging_user', None)
        super(PropertyImage, self).__init__(*args, **kwargs)
        if image_file:
            self.save()
            self.update_image(image_file)
            self.save()
        if logging_user:
            PropertyChangeLogEntry(change_type='property_image_upload', user=logging_user,
                                   parent_property=self.parent_property, new_value=self.id).save()

    def __unicode__(self):
        return 'Image: {0}'.format(self.description)

    def delete(self, using=None, keep_parents=False, logging_user=None):
        try:
            if self.image_file_name:  # TODO validate of self.image_file_name exists before attempting remove
                os.remove(self.image_path)
        except (IOError, WindowsError):
            pass
        if logging_user:
            PropertyChangeLogEntry(change_type='property_image_remove', user=logging_user,
                                   parent_property=self.parent_property, old_value=self.description).save()
        super(PropertyImage, self).delete(using=using, keep_parents=keep_parents)

    @property
    def image_path(self):
        return '{0}/{1}'.format(self.images_dir, self.image_file_name)

    def update_image(self, image):
        try:
            if self.image_file_name:
                os.remove(self.image_path)
        except (IOError, WindowsError):
            pass
        self.image_file_name = '{0}.{1}'.format(self.id, image.name.split('.', 1)[-1:][0])
        with open(self.image_path, 'wb') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

    def set_description(self, new_description, logging_user=None):
        old_description = self.description
        self.description = new_description
        self.save()
        if logging_user:
            PropertyChangeLogEntry(change_type='property_image_description_changed', user=logging_user,
                                   parent_property=self.parent_property, attribute=self.id,
                                   new_value=self.description, old_value=old_description, proxy_class='PropertyImage',
                                   proxy_source_field='id', proxy_target_field='image_url').save()

    @property
    def image_url(self):
        return '/crm/propiedad/{0}/imagenes/{1}'.format(self.parent_property.id, self.id)

    @property
    def image(self):
        try:
            return open(self.image_path, 'rb')
        except IOError:
            return None


class PropertyChangeLogEntry(models.Model, ChangeLogEntry):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    parent_property = models.ForeignKey(Property, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('Timestamp', default=timezone.now)
    type = models.ForeignKey(ChangeLogEntryType, null=True, blank=True, on_delete=models.SET_NULL)
    attribute = models.CharField('Atributo', max_length=50)
    old_value = models.CharField('Viejo valor', null=True, blank=True, max_length=20000)
    new_value = models.CharField('Nuevo valor', null=True, blank=True, max_length=20000)
    proxy_class = models.CharField('Clase intermediaria', null=True, blank=True, max_length=50)
    proxy_source_field = models.CharField('Campo origen de clase intermediaria', null=True, blank=True, max_length=50)
    proxy_target_field = models.CharField('Campo destino de clase intermediaria', null=True, blank=True, max_length=50)

    def __init__(self, *args, **kwargs):
        self.custom_constructor(*args, **kwargs)

    @property
    def html_short_description(self):
        if self.contact_property_rel_creation:
            return u'<b>{0}</b> vinculado como <b>{1}</b>'.format(self.get_contact, u'dueño'
                                                                  if self.attribute == 'owner' else u'interesado')
        elif self.contact_property_rel_edition:
            contact = self.get_contact
            return u'Comentarios editados de vínculo con <b>{0} ({1})</b>'.format(contact if contact else
                                                                                  self.unknown_contact, u'dueño'
                                                                                  if self.attribute.split('-', 1)[1]
                                                                                     == 'owner' else u'interesado')
        elif self.contact_property_rel_destruction:
            return u'<b>{0}</b> <u>des</u>vinculado como <b>{1}</b>'.format(self.get_contact, u'dueño'
                                                                            if self.attribute == 'owner'
                                                                            else u'interesado')

        return super(PropertyChangeLogEntry, self).html_short_description

    @property
    def html_details_title(self):
        if self.creation:
            return u'Creación de la propiedad {0} por {1}'.format(self.parent_property, self.user_full_name)
        if self.edition:
            return u'Edición de campo {0} de la propiedad por {1}'.format(
                self.attribute_friendly_name_map[self.attribute], self.user_full_name)
        if self.contact_property_rel_edition:
            return u'Edición de comentarios de relación con contacto por {0}'.format(self.user_full_name)

        return super(PropertyChangeLogEntry, self).html_details_title


class ContactPropertyRelationshipType(models.Model):
    description = models.CharField(u'Descripción', max_length=50)

    def __unicode__(self):
        return self.description


class ContactPropertyRelationship(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    parent_property = models.ForeignKey(Property, on_delete=models.CASCADE)
    type = models.ForeignKey(ContactPropertyRelationshipType, on_delete=models.CASCADE)
    commentary = models.CharField(u'Cometarios', null=True, blank=True, max_length=20000)
    last_modified_datetime = models.DateTimeField(u'Última modificación', default=timezone.now)

    type_owner_description = u'Dueño'
    type_interested_description = u'Interesado'

    def __init__(self, *args, **kwargs):
        if 'type_desc' in kwargs.keys():
            if kwargs['type_desc'] in ['owner', 'interested']:
                kwargs.pop('type_id', None)
                kwargs.pop('type', None)
                type_desc = self.type_owner_description if kwargs['type_desc'] == 'owner' \
                    else self.type_interested_description
                kwargs['type'] = ContactPropertyRelationshipType.objects.get(description=type_desc)
                kwargs.pop('type_desc', None)
            else:
                raise ValueError('type_desc must be one of \'owner\' or \'interested\'')

        logging_user = None
        if 'logging_user' in kwargs.keys():
            logging_user = kwargs.pop('logging_user', None)

        super(ContactPropertyRelationship, self).__init__(*args, **kwargs)

        if logging_user:
            ContactChangeLogEntry(change_type='contact_property_rel_creation', user=logging_user, contact=self.contact,
                                  attribute='owner' if self.owner else 'interested', new_value=self.parent_property.id)\
                .save()
            PropertyChangeLogEntry(change_type='contact_property_rel_creation', user=logging_user,
                                   parent_property=self.parent_property,
                                   attribute='owner' if self.owner else 'interested', new_value=self.contact.id).save()

    def __unicode__(self):
        return '{0} - {1} ({2})'.format(self.contact, self.parent_property, self.type)

    def delete(self, using=None, keep_parents=False, logging_user=None):
        if logging_user:
            ContactChangeLogEntry(change_type='contact_property_rel_destruction', user=logging_user,
                                  contact=self.contact, attribute='owner' if self.owner else 'interested',
                                  old_value=self.parent_property.id).save()
            PropertyChangeLogEntry(change_type='contact_property_rel_destruction', user=logging_user,
                                   parent_property=self.parent_property,
                                   attribute='owner' if self.owner else 'interested', old_value=self.contact.id).save()
        super(ContactPropertyRelationship, self).delete(using=using, keep_parents=keep_parents)

    def set_commentary(self, new_commentary, logging_user=None):
        old_commentary = self.commentary
        self.commentary = new_commentary
        self.last_modified_datetime = timezone.now()
        self.save()
        ContactChangeLogEntry(change_type='contact_property_rel_edition', user=logging_user, contact=self.contact,
                              attribute=u'{0}-{1}'.format(self.parent_property.id, u'owner' if self.owner
                                                          else u'interested'), new_value=self.commentary,
                              old_value=old_commentary).save()
        PropertyChangeLogEntry(change_type='contact_property_rel_edition', user=logging_user,
                               parent_property=self.parent_property, attribute=u'{0}-{1}'.format(self.contact.id,
                                                                                                 u'owner' if self.owner
                                                                                                 else u'interested'),
                               new_value=self.commentary, old_value=old_commentary).save()

    @property
    def owner(self):
        return self.type.description == self.type_owner_description

    @property
    def interested(self):
        return self.type.description == self.type_interested_description


class NotificationTone(models.Model):
    name = models.CharField(u'Nombre', unique=True, max_length=50)
    file_name = models.CharField(u'Nombre de archivo', unique=True, max_length=50)

    mime_types = {
        'mp3': 'audio/mpeg3',
        'ogg': 'audio/ogg'
    }

    @classmethod
    def default_notification_tone(cls):
        return cls.objects.get(name='You wouldn\'t believe')

    @classmethod
    def default_message_tone(cls):
        return cls.objects.get(name='All eyes on me')

    def file_path(self, extension='mp3'):
        if self.id:
            return '{0}{1}/{2}.{3}'.format(settings.MEDIA_URL, 'notifications_tones', self.file_name, extension)

        return None

    def file_url(self, extension='mp3'):
        if self.id:
            return '/crm/tonos/{0}/{1}'.format(extension, self.id)

        return None

    @property
    def mp3_url(self):
        return self.file_url(extension='mp3')

    @property
    def ogg_url(self):
        return self.file_url(extension='ogg')


class NotificationType(models.Model):
    description = models.CharField(u'Descripción', null=True, blank=True, max_length=50)
    order_index = models.IntegerField(u'Orden', null=True, blank=True)
    is_massive = models.BooleanField('Masiva', default=False)

    def __unicode__(self):
        return u'Tipo de notificación {0}'.format(self.description)


notification_types = {
    'property_in_charge_changed': NotificationType.objects.get(description=u'Modificación de propiedad a cargo').id,
    'contact_in_charge_changed': NotificationType.objects.get(description=u'Modificación de contacto a cargo').id,
    'property_assigned': NotificationType.objects.get(description=u'Asignación de propiedad a cargo').id,
    'property_unassigned': NotificationType.objects.get(description=u'Desasignación de propiedad a cargo').id,
    'contact_assigned': NotificationType.objects.get(description=u'Asignación de contacto a cargo').id,
    'contact_unassigned': NotificationType.objects.get(description=u'Desasignación de contacto a cargo').id,
    'property_created': NotificationType.objects.get(description=u'Creación de propiedad en tu empresa').id,
    'contact_created': NotificationType.objects.get(description=u'Creación de contacto en tu empresa').id,
    'property_removed': NotificationType.objects.get(description=u'Eliminación de propiedad en tu empresa').id,
    'contact_removed': NotificationType.objects.get(description=u'Eliminación de contacto en tu empresa').id,
    'property_in_charge_removed': NotificationType.objects.get(description=u'Eliminación de propiedad a cargo').id,
    'contact_in_charge_removed': NotificationType.objects.get(description=u'Eliminación de contacto a cargo').id
}


class NotificationConfig(object):
    @property
    def take_action(self):
        return self.notify or self.email

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'notification_type': self.notification_type.description,
            'type_id': self.notification_type_id,
            'notify': self.notify,
            'email': self.email,
            'can_view': self.can_view,
            'can_edit': self.can_edit
        }


class UserNotificationConfig(models.Model, NotificationConfig):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    notify = models.BooleanField('Notificarme', default=True)
    email = models.BooleanField('Enviarme email', default=True)
    can_view = models.BooleanField('Puede ver', default=True)
    can_edit = models.BooleanField('Puede editar', default=True)

    @property
    def to_dict(self):
        return merge_two_dicts(super(GroupNotificationConfig, self).to_dict, {
            'user': self.user.full_name,
            'username': self.user.username,
            'user_id': self.user_id
        })

    def __init__(self, *args, **kwargs):
        notification_type_id = None
        if 'notification_type' in kwargs.keys():
            notification_type_id = kwargs['notification_type'].id
        if 'notification_type_id' in kwargs.keys():
            notification_type_id = kwargs['notification_type_id']

        user = kwargs['user'] if 'user' in kwargs.keys() else None

        if notification_type_id and user:
            group_config = user.group_notification_config(user.company, notification_type_id)
            kwargs['can_view'] = group_config.can_view
            kwargs['can_edit'] = group_config.can_edit
        super(UserNotificationConfig, self).__init__(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, group_config=None):
        if not group_config:
            group_config = self.user.group_notification_config(self.user.company, self.notification_type.id)
        self.can_view = group_config.can_view
        self.can_edit = group_config.can_edit
        if not self.can_edit:
            self.notify = group_config.notify
            self.email = group_config.email
        super(UserNotificationConfig, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                                 update_fields=update_fields)


class GroupNotificationConfig(models.Model, NotificationConfig):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    notification_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    notify = models.BooleanField('Notificarme', default=True)
    email = models.BooleanField('Enviarme email', default=True)
    can_view = models.BooleanField('Puede ver', default=True)
    can_edit = models.BooleanField('Puede editar', default=True)

    @property
    def to_dict(self):
        return merge_two_dicts(super(GroupNotificationConfig, self).to_dict, {
            'company': self.company.name,
            'company_id': self.company_id,
            'group': self.group.name,
            'group_id': self.group_id
        })

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None,
             overwrite_user_configs=False):
        super(GroupNotificationConfig, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                                  update_fields=update_fields)
        for user_config in [uc for uc in [u.notification_config(None, id=self.notification_type.id,
                                                                only_user_configuration=True)
                                          for u in self.group.user_set.all()] if uc]:

            if overwrite_user_configs:
                user_config.delete()
            else:
                user_config.save(group_config=self)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    type = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    related_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='related_user')
    related_property = models.ForeignKey(Property, null=True, blank=True, on_delete=models.SET_NULL)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField('Timestamp', default=timezone.now)
    seen = models.BooleanField('Visto', default=False)
    details = models.CharField('Detalles', null=True, blank=True, max_length=4000)

    unknown_username = u'Usuario eliminado'
    unknown_property = u'Propiedad eliminada'
    unknown_contact = u'Contacto eliminado'

    def __unicode__(self):
        return 'Notificación - {0} {1} {2} - {3}'.format(self.user, self.type.description, self.timestamp,
                                                         'Vista' if self.seen else 'No vista')

    def get_attr_if_exists(self, attr, default=None, format_string=None):
        value = eval('self.{0} if self.{1} else \'{2}\''.format(attr, attr.split('.')[0], default))
        if format_string and value != default:
            return format_string.format(value)
        return value

    @property
    def time_ago(self):
        return time_ago(self.timestamp)

    @property
    def data(self):
        if self.type_id == notification_types['property_in_charge_changed']:
            return {
                'title': u'Tu propiedad fue modificada',
                'short_description': u'{0} modificada por {1}'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'La propiedad {0} a su cargo fue modificada por el usuario {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:property', args=(self.related_property.id, ))
                if self.related_property else u'',
                'image_url': self.related_property.cover_image.image_url
                if self.related_property and self.related_property.cover_image
                else '/static/collaborative_crm/images/misc/default_property.png'
            }
        elif self.type_id == notification_types['contact_in_charge_changed']:
            return {
                'title': u'Tu contacto fue modificado',
                'short_description': u'{0} modificado por {1}'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'El contacto {0} a su cargo fue modificada por el usuario {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:contact', args=('contacto', self.contact.id)) if self.contact
                else u'',
                'image_url': '/static/collaborative_crm/images/misc/default_user.png'
            }
        elif self.type_id == notification_types['property_assigned']:
            return {
                'title': u'Asignado a propiedad',
                'short_description': u'Asignado a {0} por {1}'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'Usted fue asignado a cargo de la propiedad {0} por {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:property', args=(self.related_property.id, ))
                if self.related_property else u'',
                'image_url': self.related_property.cover_image.image_url
                if self.related_property and self.related_property.cover_image
                else '/static/collaborative_crm/images/misc/default_property.png'
            }
        elif self.type_id == notification_types['property_unassigned']:
            return {
                'title': u'Desasignado de propiedad',
                'short_description': u'Desasignado de {0} por {1}'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'Usted fue quitado del cargo de la propiedad {0} por {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:property', args=(self.related_property.id, ))
                if self.related_property else u'',
                'image_url': self.related_property.cover_image.image_url
                if self.related_property and self.related_property.cover_image
                else '/static/collaborative_crm/images/misc/default_property.png'
            }
        elif self.type_id == notification_types['contact_assigned']:
            return {
                'title': u'Asignado a contacto',
                'short_description': u'Asignado a {0} por {1}'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'Usted fue asignado a cargo del contacto {0} por {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:contact', args=('contacto', self.contact.id)) if self.contact
                else u'',
                'image_url': '/static/collaborative_crm/images/misc/default_user.png'
            }
        elif self.type_id == notification_types['contact_unassigned']:
            return {
                'title': u'Desasignado de contacto',
                'short_description': u'Desasignado de {0} por {1}'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'Usted fue quitado del cargo del contacto {0} por {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:contact', args=('contacto', self.contact.id)) if self.contact
                else u'',
                'image_url': '/static/collaborative_crm/images/misc/default_user.png'
            }
        elif self.type_id == notification_types['property_created']:
            return {
                'title': u'Propiedad creada',
                'short_description': u'{0} creada por {1}'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'La propiedad {0} fue creada en su empresa por el usuario {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('related_property', self.unknown_property),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:property', args=(self.related_property.id, ))
                if self.related_property else u'',
                'image_url': self.related_property.cover_image.image_url
                if self.related_property and self.related_property.cover_image
                else '/static/collaborative_crm/images/misc/default_property.png'
            }
        elif self.type_id == notification_types['contact_created']:
            return {
                'title': u'Contacto creado',
                'short_description': u'{0} creado por {1}'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'El contacto {0} fue creado en su empresa por el usuario {1}{2} a las {3}.'.format(
                    self.get_attr_if_exists('contact', self.unknown_contact),
                    self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': reverse('collaborative_crm:contact', args=('contacto', self.contact.id)) if self.contact
                else u'',
                'image_url': '/static/collaborative_crm/images/misc/default_user.png'
            }
        elif self.type_id == notification_types['property_removed']:
            return {
                'title': u'Propiedad eliminada',
                'short_description': u'{0} eliminada por {1}'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'La propiedad {0} fue eliminada de su empresa por el usuario {1}{2} a las {3}.'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': '',
                'image_url': '/static/collaborative_crm/images/misc/default_property.png'
            }
        elif self.type_id == notification_types['contact_removed']:
            return {
                'title': u'Contacto eliminado',
                'short_description': u'{0} eliminado por {1}'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'El contacto {0} fue eliminado de su empresa por el usuario {1}{2} a las {3}.'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': '',
                'image_url': '/static/collaborative_crm/images/misc/default_user.png'
            }
        elif self.type_id == notification_types['property_in_charge_removed']:
            return {
                'title': u'Tu propiedad fue eliminada',
                'short_description': u'{0} eliminada por {1}'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'La propiedad {0} a su cargo fue eliminada por el usuario {1}{2} a las {3}.'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': '',
                'image_url': '/static/collaborative_crm/images/misc/default_property.png'
            }
        elif self.type_id == notification_types['contact_in_charge_removed']:
            return {
                'title': u'Tu contacto fue eliminado',
                'short_description': u'{0} eliminado por {1}'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username)),
                'description': u'El contacto {0} a su cargo fue eliminado por el usuario {1}{2} a las {3}.'.format(
                    self.details, self.get_attr_if_exists('related_user.full_name', self.unknown_username),
                    self.get_attr_if_exists('related_user.username', u'', format_string=' ({0})'),
                    self.timestamp.time().strftime('%H:%M:%S')),
                'url': '',
                'image_url': '/static/collaborative_crm/images/misc/default_user.png'
            }

        return {
            'title': u'Notificación desconocida',
            'short_description': u'Notificación desconocida',
            'description': u'Notificación desconocida',
            'url': '',
            'image_url': None
        }

    def get_similar_notifications(self, order_by=None, first=False):
        kwargs = {}
        if self.related_property:
            kwargs['related_property'] = self.related_property
        if self.contact:
            kwargs['contact'] = self.contact
        if order_by:
            notifs = Notification.objects.filter(
                user=self.user, type=self.type, related_user=self.related_user, **kwargs).order_by(order_by)
        else:
            notifs = Notification.objects.filter(
                user=self.user, type=self.type, related_user=self.related_user, **kwargs)
        if first:
            return notifs.first()
        else:
            return notifs

    @property
    def notified_and_related_user_are_the_same(self):
        # Notifications require the notified user and the related user to be different, if not, then they are dismissed
        return self.user == self.related_user

    @property
    def dismiss_conditions(self):
        return [dc for dc in [self.notified_and_related_user_are_the_same] if dc]

    @property
    def occurred_within_last_24_hs(self):
        # If these types of notifications already occurred within the last 24Hs, they are dismissed
        if self.type_id in (notification_types['property_in_charge_changed'],
                            notification_types['contact_in_charge_changed']):

            notif = self.get_similar_notifications(order_by='-timestamp', first=True)
            return notif if notif and notif.timestamp >= self.timestamp - timedelta(hours=24) else None

        return None

    @property
    def update_conditions(self):
        return [self.occurred_within_last_24_hs]

    @property
    def should_notify(self):
        return not self.dismiss_conditions and not self.should_update

    @property
    def should_update(self):
        return len([uc for uc in self.update_conditions if uc]) > 0

    def update(self, host_url=None):
        for notification in self.update_conditions:
            if notification:
                notification.timestamp = self.timestamp
                notification.seen = False
                notification.save()
                notification.broadcast(host_url)

    @property
    def show_notification(self):
        return self.user.notification_config(None, id=self.type.id).notify

    def email(self, host_url, only_if_should_notify=True):
        if settings.EMAIL_NOTIFICATIONS and (self.should_notify or not only_if_should_notify):
            context = {
                'notification': self,
                'url': (host_url + self.data['url']) if self.data['url'] else None,
                'link_to_login': host_url + reverse('login_page'),
                'linked_prop_email': linked_prop_email,
                'linked_prop_telephone': linked_prop_telephone
            }
            template = loader.get_template('collaborative_crm/email_notification.html')
            template_plain = loader.get_template('collaborative_crm/email_notification.txt')
            create_html_plain_email(u'[LinkedProp] Aviso de {0}'.format(self.type.description),
                                    template_plain.render(context, None), template.render(context, None),
                                    [self.user.username]).send()

    def broadcast(self, host_url=None):
        ChannelGroup('updates-channel-user-%s' % self.user.id).send({
            'text': json.dumps({
                'update_type': 'notification',
                'notification_id': self.id,
                'title': self.data['title'],
                'short_description': self.data['short_description'],
                'fully_qualified_url': (host_url + self.data['url']) if host_url and self.data['url'] else None,
                'image_src': host_url + self.data['image_url'],
                'html': loader.get_template('collaborative_crm/notifications.html').render({'user': self.user})
            })
        })

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, only_if_should_notify=False,
             host_url=None):
        if not only_if_should_notify or self.should_notify:
            super(Notification, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                           update_fields=update_fields)
            if only_if_should_notify:
                self.broadcast(host_url)

        if only_if_should_notify and self.should_update:
            self.update(host_url)


class Conversation(models.Model):
    title = models.CharField(u'Título', null=True, blank=True, max_length=100)
    users = models.ManyToManyField(User, through='ConversationUser')
    created = models.DateTimeField(u'Creada', default=timezone.now)

    def __init__(self, *args, **kwargs):
        users_to_add = kwargs.pop('users') if 'users' in kwargs.keys() else []
        super(Conversation, self).__init__(*args, **kwargs)
        if users_to_add:
            self.save()
            for user in users_to_add:
                ConversationUser(conversation=self, user=user).save()

    def __unicode__(self):
        return self.get_title

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.get_title,
            'users': [u.to_dict for u in self.users.all()],
            'latest_activity': self.latest_activity.strftime('%d/%m/%Y %H:%M:%S'),
            'created': self.created.strftime('%d/%m/%Y %H:%M:%S')
        }

    @property
    def url(self):
        return reverse('collaborative_crm:messages', args=(self.id, ))

    @property
    def generate_title(self):
        return u'Conversación'

    @property
    def get_title(self):
        return self.title if self.title else self.generate_title

    def add_user(self, user):
        now = timezone.now()
        if user not in self.users:
            self.users.add(user)
            self.save()
            for msg in self.message_set.all():
                msg.users_to.create(user=user, seen=now)

    def remove_user(self, user):
        if user in self.users:
            for msg in self.message_set.all():
                if msg.user_from == user:
                    msg.user_from = None
                else:
                    msg.users_to.filter(user_to=user).delete()
                msg.save()
            self.users.remove(user)
            self.save()

    @property
    def latest_message(self):
        return self.message_set.order_by('-timestamp').first()

    @property
    def latest_activity(self):
        return self.latest_message.timestamp if self.latest_message else self.created

    @property
    def time_ago(self):
        return self.latest_message.time_ago if self.latest_message else time_ago(self.created)

    def unred_messages(self, user):
        return self.message_set.filter(messageuserto__user_to=user, messageuserto__red=None)

    def send_message(self, user_from, content, broadcast=True, request=None):
        msg = Message(conversation=self, user_from=user_from, content=content)
        msg.save()
        self.message_set.add(msg)
        for user_to in self.users.all().exclude(id=user_from.id):
            MessageUserTo(message=msg, user_to=user_to).save()
        if broadcast:
            msg.broadcast('https' if request.is_secure() else 'http' + '://' + request.get_host())
        return msg

    def user_read_all_messages(self, user, timestamp=None):
        now = timestamp if timestamp else timezone.now()
        for msg in self.unred_messages(user):
            msg_user_to = msg.messageuserto_set.filter(user_to=user).first()
            msg_user_to.red = now
            msg_user_to.save()


class ConversationUser(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'{0} - Usuario: {1}'.format(self.conversation, self.user.full_name)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user_from = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_from')
    users_to = models.ManyToManyField(User, through='MessageUserTo', related_name='users_to')
    content = models.CharField(u'Contenido', default=u'', max_length=4000)
    timestamp = models.DateTimeField(u'Timestamp', default=timezone.now)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.user_from.full_name, self.content)

    @property
    def to_dict(self):
        return {
            'user_from': self.user_from.to_dict,
            'content': self.content,
            'timestamp': utc_to_local(self.timestamp).strftime('%d/%m/%Y %H:%M:%S')
        }

    def seen(self, user, timestamp=None):
        user_to = self.users_to.filter(user_to=user).first()
        user_to.seen = timestamp if timestamp else timezone.now()
        user_to.save()

    @property
    def time_ago(self):
        return time_ago(self.timestamp)

    def broadcast(self, host_url=None):
        for user in [self.user_from] + list(self.users_to.all()):
            ChannelGroup('updates-channel-user-%s' % user.id).send({
                'text': json.dumps({
                    'update_type': 'message',
                    'message_id': self.id,
                    'conversation_id': self.conversation.id,
                    'conversation': self.conversation.title,
                    'from_id': self.user_from.id,
                    'from': self.user_from.full_name_reversed,
                    'content': self.content,
                    'timestamp': utc_to_local(self.timestamp).strftime('%d/%m/%Y %H:%M:%S'),
                    'fully_qualified_url': (host_url + self.conversation.url) if host_url else None,
                    'image_src': host_url + '/static/collaborative_crm/images/misc/message.png',
                    'html': loader.get_template('collaborative_crm/messages_box.html').render({'user': user}),
                    'conversations_html': loader.get_template('collaborative_crm/conversations_box.html')
                                          .render({'conversations': sorted(user.conversations(),
                                                                           key=lambda conv: conv.latest_activity,
                                                                           reverse=True), 'user': user})
                })
            })


class MessageUserTo(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, on_delete=models.CASCADE)
    red = models.DateTimeField(u'Leído', null=True, blank=True)

    def __unicode__(self):
        return u'Mensaje \'{0}\' a {1} ({2})'.format(self.message, self.user_to.full_name,
                                                     u'leído {0}'.format(self.red) if self.red else u'No leído ')


class UserInChargeUser(models.Model):
    user_in_charge = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_user')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_user')


# User model custom methods
@property
def full_name(self):
    if self.last_name and self.first_name:
        return u'{0}, {1}'.format(self.last_name, self.first_name)
    elif self.last_name:
        return self.last_name
    elif self.first_name:
        return self.first_name
    return self.username


@property
def full_name_reversed(self):
    if self.last_name and self.first_name:
        return u'{0} {1}'.format(self.first_name, self.last_name)
    elif self.last_name:
        return self.last_name
    elif self.first_name:
        return self.first_name
    return self.username


@property
def company(self):
    return self.userextension.company


@property
def telephone_number(self):
    return self.userextension.telephone_number


@property
def add_new_users_to_my_charge(self):
    return self.userextension.add_new_users_to_my_charge


@property
def add_my_branch_users_to_my_charge(self):
    return self.userextension.add_my_branch_users_to_my_charge


@property
def main_branch(self):
    return self.userextension.main_branch


def set_main_branch(self, main_branch_id):
    if int(main_branch_id if main_branch_id else 0):
        old_branch_id = self.main_branch.id if self.main_branch else 0
        self.userextension.main_branch_id = int(main_branch_id)
        self.userextension.save()
        if main_branch_id != old_branch_id:
            for user in self.company.users_with_automatic_add_in_charge_when_main_branch_set\
                    .filter(userextension__main_branch_id=main_branch_id):
                user.add_user_in_charge(self)
    else:
        self.userextension.main_branch_id = None
    self.userextension.save()


@property
def groups_names_list(self):
    return self.groups.values_list('name', flat=True)


@property
def first_group_name(self):
    return self.groups_names_list[0]


@property
def is_super_agent(self):
    return self.groups.first().is_super_agent


@property
def is_admin(self):
    return self.groups.first().is_admin


@property
def to_dict(self):
    return {
        'id': self.id,
        'username': self.username,
        'full_name': self.full_name,
        'first_group': self.first_group_name,
        'first_group_id': self.groups.all()[0].id,
        'first_name': self.first_name,
        'last_name': self.last_name,
        'telephone_number': self.telephone_number,
        'email': self.email,
        'main_branch': self.main_branch.name if self.main_branch else None,
        'main_branch_id': self.main_branch.id if self.main_branch else None,
        'users_in_charge_ids': [u.user.id for u in self.users_in_charge],
        'is_super_agent': self.is_super_agent,
        'add_new_users_to_my_charge': self.add_new_users_to_my_charge,
        'add_my_branch_users_to_my_charge': self.add_my_branch_users_to_my_charge
    }


@staticmethod
def generate_random_password(chars=20):
    return ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(chars))


def full_name_with_text_search_matches(self, search_term):
    return self.userextension.full_name_with_text_search_matches(search_term)


def email_with_text_search_matches(self, search_term):
    return self.userextension.email_with_text_search_matches(search_term)


def text_search_score(self, search_term):
    return self.userextension.text_search_score(search_term)


@property
def login_attempts_remaining(self):
    return self.userextension.login_attempts


def failed_login(self):
    if self.userextension.login_attempts > 0:
        self.userextension.login_attempts -= 1
    if self.userextension.login_attempts == 0:
        self.is_active = False
        self.save()
    self.userextension.save()


def successful_login(self):
    self.userextension.login_attempts = 5
    self.userextension.save()
    for s in [sess for sess in Session.objects.all() if int(sess.get_decoded().get('_auth_user_id', 0)) == self.id]:
        s.delete()


def notification_config(self, notification_type, id=None, only_user_configuration=False):
    notification_type_id = notification_types[notification_type] if notification_type and not id else id
    config = self.usernotificationconfig_set.filter(notification_type_id=notification_type_id).first()
    if not config and not only_user_configuration:
        return self.group_notification_config(notification_type, id=id)

    return config


def group_notification_config(self, notification_type, id=None):
    return self.groups.first().notification_config(self.company, notification_type, id=id)


def notify(self, notification_type, related_user, data={}, request=None, host_url=None):
    if settings.NOTIFICATIONS:
        if not host_url:
            host_url = request.build_absolute_uri('/')[:-1]

        Channel('notify_user').send({
            'user_id': self.id,
            'notification_type': notification_type,
            'related_user_id': related_user.id,
            'data': data,
            'host_url': host_url
        })


def notifications(self, unseen_only=False, last_n=None, starting_at=None, only_to_show=False):
    kwargs = {'seen': False} if unseen_only else {}
    if only_to_show:
        return [n for n in Notification.objects.filter(user=self, **kwargs).order_by('-timestamp')
                if n.show_notification][starting_at:last_n]
    else:
        return Notification.objects.filter(user=self, **kwargs).order_by('-timestamp')[starting_at:last_n]


@property
def notifications_last_15_to_show(self):
    return self.notifications(last_n=15, only_to_show=True)


@property
def unseen_notifications(self):
    return self.notifications(unseen_only=True)


def conversations(self, last_n=None, starting_at=None, filters={}, first=False):
    def sorting_function(lst):
        return sorted(lst, key=lambda c: c.latest_activity, reverse=True)

    query = Conversation.objects.filter(conversationuser__user=self, **filters)
    if first:
        return query.first()

    return sorting_function(query)[starting_at:last_n]


@property
def conversations_last_15(self):
    return self.conversations(last_n=15)


@property
def unred_messages_count(self):
    return sum([len(c.unred_messages(self)) for c in self.conversations()])


def add_user_in_charge(self, user):
    if self != user and not UserInChargeUser.objects.filter(user_in_charge=self, user=user).first():
        UserInChargeUser(user_in_charge=self, user=user).save()


def set_users_in_charge(self, users):
    users = [u for u in users if u.company == self.company and u != self]
    UserInChargeUser.objects.filter(user_in_charge=self).exclude(user_id__in=[u.id for u in users]).delete()
    for user in [u for u in users if not UserInChargeUser.objects.filter(user_in_charge=self, user=u).first()]:
        self.add_user_in_charge(user)


@property
def users_in_charge(self):
    return UserInChargeUser.objects.filter(user_in_charge=self)


def in_charge_of_user(self, user):
    return self.is_super_agent and self.users_in_charge.filter(user=user).first()


def permissions_over_user(self, user):
    return not user or self.is_admin or self == user or self.company.user_has_access_user(self, user) or \
           self.in_charge_of_user(user)


def permissions_over_property(self, property):
    return property.__class__ == Property and (not property.user or self.permissions_over_user(property.user))


def permissions_over_contact(self, contact):
    return contact.__class__ == Contact and (not contact.user or self.permissions_over_user(contact.user))


@property
def notifications_tone(self):
    return self.userextension.notifications_tone


@property
def messages_tone(self):
    return self.userextension.messages_tone


text_search_relevant_fields = ['username', 'first_name', 'last_name']
text_search_operation = '__unaccent__icontains'

auth.models.User.add_to_class('full_name', full_name)
auth.models.User.add_to_class('full_name_reversed', full_name_reversed)
auth.models.User.add_to_class('company', company)
auth.models.User.add_to_class('telephone_number', telephone_number)
auth.models.User.add_to_class('add_new_users_to_my_charge', add_new_users_to_my_charge)
auth.models.User.add_to_class('add_my_branch_users_to_my_charge', add_my_branch_users_to_my_charge)
auth.models.User.add_to_class('main_branch', main_branch)
auth.models.User.add_to_class('set_main_branch', set_main_branch)
auth.models.User.add_to_class('groups_names_list', groups_names_list)
auth.models.User.add_to_class('first_group_name', first_group_name)
auth.models.User.add_to_class('is_super_agent', is_super_agent)
auth.models.User.add_to_class('is_admin', is_admin)
auth.models.User.add_to_class('to_dict', to_dict)
auth.models.User.add_to_class('generate_random_password', generate_random_password)
auth.models.User.add_to_class('full_name_with_text_search_matches', full_name_with_text_search_matches)
auth.models.User.add_to_class('email_with_text_search_matches', email_with_text_search_matches)
auth.models.User.add_to_class('text_search_score', text_search_score)
auth.models.User.add_to_class('text_search_relevant_fields', text_search_relevant_fields)
auth.models.User.add_to_class('text_search_operation', text_search_operation)
auth.models.User.add_to_class('login_attempts_remaining', login_attempts_remaining)
auth.models.User.add_to_class('failed_login', failed_login)
auth.models.User.add_to_class('successful_login', successful_login)
auth.models.User.add_to_class('notification_config', notification_config)
auth.models.User.add_to_class('group_notification_config', group_notification_config)
auth.models.User.add_to_class('notify', notify)
auth.models.User.add_to_class('notifications', notifications)
auth.models.User.add_to_class('notifications_last_15_to_show', notifications_last_15_to_show)
auth.models.User.add_to_class('unseen_notifications', unseen_notifications)
auth.models.User.add_to_class('conversations', conversations)
auth.models.User.add_to_class('conversations_last_15', conversations_last_15)
auth.models.User.add_to_class('unred_messages_count', unred_messages_count)
auth.models.User.add_to_class('add_user_in_charge', add_user_in_charge)
auth.models.User.add_to_class('set_users_in_charge', set_users_in_charge)
auth.models.User.add_to_class('users_in_charge', users_in_charge)
auth.models.User.add_to_class('in_charge_of_user', in_charge_of_user)
auth.models.User.add_to_class('permissions_over_user', permissions_over_user)
auth.models.User.add_to_class('permissions_over_property', permissions_over_property)
auth.models.User.add_to_class('permissions_over_contact', permissions_over_contact)
auth.models.User.add_to_class('notifications_tone', notifications_tone)
auth.models.User.add_to_class('messages_tone', messages_tone)
# User model custom methods


# Group model custom methods
@property
def is_super_agent(self):
    return self.name == u'Super agente'


@property
def is_admin(self):
    return self.name == u'Admin empresa'


def notification_config(self, company, notification_type, id=None):
    notification_id = notification_types[notification_type] if notification_type and not id else id
    return GroupNotificationConfig.objects.filter(group=self, company=company, notification_type_id=notification_id)\
        .first()

auth.models.Group.add_to_class('is_super_agent', is_super_agent)
auth.models.Group.add_to_class('is_admin', is_admin)
auth.models.Group.add_to_class('notification_config', notification_config)
# Group model custom methods


# User model extension
class UserExtension(models.Model, ContactPropertyUserCommon):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    main_branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
    telephone_number = models.CharField(u'Teléfono', null=True, blank=True, max_length=50)
    add_new_users_to_my_charge = models.BooleanField(u'Agregar nuevos usuarios a mi cargo', default=False)
    add_my_branch_users_to_my_charge = models.BooleanField(u'Agregar usuarios de mi sucursal a mi cargo', default=False)
    notifications_tone = models.ForeignKey(NotificationTone, default=NotificationTone.default_notification_tone().id,
                                           on_delete=models.SET_DEFAULT, related_name='notifications_tone')
    messages_tone = models.ForeignKey(NotificationTone, default=NotificationTone.default_message_tone().id,
                                      on_delete=models.SET_DEFAULT, related_name='messages_tone')
    login_attempts = models.IntegerField(u'Intentos de log-in', default=5)

    def __unicode__(self):
        return u'Extensión usuario {0}'.format(self.user)

    @property
    def full_name(self):
        return self.user.full_name
# User model extension


# Extra transformers for queryset filtering (only works in PostgreSQL)
@models.DateTimeField.register_lookup
class WeekTransform(DateTransform):
    lookup_name = 'week'


@models.DateTimeField.register_lookup
class ISOYearTransform(DateTransform):
    lookup_name = 'isoyear'
# Extra transformers for queryset filtering (only works in PostgreSQL)
