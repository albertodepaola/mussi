#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q, F, Count, Max, Value
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from .models import *
from .utils import *
import json
import shutil
from datetime import datetime, timedelta


def home(request):
    return redirect('collaborative_crm:news')


@login_required
def news(request):
    template = loader.get_template('collaborative_crm/news.html')
    context = {
        'web_title': 'LinkedProp | Noticias',
        'page_title': 'Noticias',
        'page_sub_title': u'Novedades en tu empresa',
        'page_name': 'news',
        'users': request.user.company.users
    }
    return HttpResponse(template.render(context, request))


@login_required
def news_data(request):
    # TODO - Refactor
    if request.method == 'POST':
        parameters = json.loads(request.body if request.body else '{}')
        entities = parameters.get('entities', 'propiedades-contactos')
        week_from = int(parameters.get('week_from', 0))
        week_to = int(parameters.get('week_to', 3))
        users = parameters.get('users', None)
        users_in_charge = parameters.get('users_in_charge', None)
        order_by = parameters.get('order_by', None)

        template = loader.get_template('collaborative_crm/news_data.html')

        year = timezone.now().isocalendar()[0]
        week = (timezone.now() - timedelta(days=week_from * 7)).isocalendar()[1]
        week_to -= week_from

        entity_info = {
            'contactos': {'class': ContactChangeLogEntry, 'entity_field_name': 'contact'},
            'propiedades': {'class': PropertyChangeLogEntry, 'entity_field_name': 'parent_property'}
        }
        entities = [e for e in entities.split('-') if e in entity_info.keys()]

        query = []
        for entity in entities:
            filters_dict = {
                '{0}__company'.format(entity_info[entity]['entity_field_name']): request.user.company
            }

            if users:
                filters_dict['user_id__in'] = users if users != 'me' else [request.user.id]

            if users_in_charge:
                filters_dict['{0}__user_id__in'.format(entity_info[entity]['entity_field_name'])] = users_in_charge \
                    if users_in_charge != 'me' else [request.user.id]

            q = Q(**merge_two_dicts(filters_dict, {'timestamp__year': year, 'timestamp__week__lte': week,
                                                   'timestamp__week__gte': week - week_to}))

            if week <= week_to:
                q |= Q(**merge_two_dicts(filters_dict,
                                         {'timestamp__year': year - 1, 'timestamp__week__gte': 52 - week_to + week}))

            query.extend(entity_info[entity]['class'].objects.filter(q)
                         .annotate(entity=Value(entity, models.CharField()))
                         .extra(select={'week': 'date_part(\'year\', timestamp) * 100 + '
                                                'date_part(\'week\', timestamp)'})
                         .order_by(u'{0}-timestamp'.format(reduce(
                                                           lambda ob, ob_item: ob + ob_item + u', ', order_by, u'')
                                                           if order_by else u'')))

        query = [q_item for q_item in query if q_item.user_has_permissions(request.user)]
        weeks = [{'week': q_item.week} for q_item in query]
        week_order = week_from
        last_week = 0
        for week in sorted(weeks, reverse=True):
            if week['week'] != last_week:
                week['order'] = week_order
                week_order += 1
                last_week = week['week']
            else:
                weeks.remove(week)
        weeks = weeks[:week_to]

        for week in sorted(weeks, key=lambda w: w['order']):
            week['objects'] = sorted(
                [{'object': o.parent_property if o.entity == 'propiedades' else o.contact, 'entity': o.entity,
                  'latest_timestamp': o.timestamp} for o in query if o.week == week['week']],
                key=lambda elem: elem['latest_timestamp'], reverse=True)

        for week in weeks:
            objects = []
            for obj in sorted(week['objects'], key=lambda o: o['latest_timestamp'], reverse=True):
                if obj['object'] not in objects:
                    objects.append(obj['object'])
                    obj['entries'] = [q for q in query if q.week == week['week'] and
                                      (q.parent_property if q.entity == 'propiedades' else q.contact) == obj['object']]
                else:
                    week['objects'].remove(obj)

        return HttpResponse(template.render({'news': weeks}, request))

    # TODO - Refactor
    return HttpResponseForbidden()


@login_required
def contacts(request, my_contacts):
    only_my_contacts = my_contacts == 'mis_contactos'
    template = loader.get_template('collaborative_crm/contacts.html')
    context = {
        'web_title': 'LinkedProp | {0}'.format('Contactos' if not only_my_contacts else 'Mis Contactos'),
        'page_title': 'Contactos' if not only_my_contacts else 'Mis Contactos',
        'page_sub_title': u'Contactos de mi empresa' if not only_my_contacts else u'Contactos a mi cargo',
        'page_name': 'contact',
        'my_contacts': only_my_contacts,
        'neighborhoods': Neighborhood.objects.all()
    }
    return HttpResponse(template.render(context, request))


@login_required
def contact(request, new_contact='nuevo_contacto', contact_id_name_property_relationship_type=None, property_id=None):
    template = loader.get_template('collaborative_crm/contact.html')
    new_contact = (new_contact == 'nuevo_contacto')
    related_property = (contact_id_name_property_relationship_type in ['dueno', 'interesado'] and property_id)

    if new_contact:
        contact = Contact(first_name='', last_name='', telephone_number='', email='')
        contact.id = 0
    else:
        try:
            contact = Contact.objects.get(id=int(contact_id_name_property_relationship_type),
                                          company=request.user.company)
        except Contact.DoesNotExist:
            return redirect('collaborative_crm:contact', 'nuevo_contacto')

    first_name = ''
    last_name = ''
    property_relationship_type = None
    property = None
    if related_property:
        property = Property.objects.get(id=int(property_id))
        property_relationship_type_map = {
            'dueno': 'owner',
            'interesado': 'interested'
        }
        property_relationship_type = property_relationship_type_map[contact_id_name_property_relationship_type]
    else:
        if contact.id == 0 and contact_id_name_property_relationship_type:
            first_name = contact_id_name_property_relationship_type.split(' ', 1)[0]
            try:
                last_name = contact_id_name_property_relationship_type.split(' ', 1)[1]
            except IndexError:
                pass

    for notification in Notification.objects.filter(user=request.user, contact=contact, seen=False):
        notification.seen = True
        notification.save()

    all_history = contact.contactchangelogentry_set.all()

    context = {
        'web_title': u'LinkedProp | Contacto - {0}'.format(contact) if contact.id != 0
        else 'LinkedProp | Nuevo contacto',
        'page_title': u'{0}. {1}'.format(contact.id, contact) if contact.id != 0 else 'Nuevo contacto',
        'page_sub_title': u'Página de contacto',
        'page_name': 'contact',
        'contact': contact,
        'can_edit': request.user.permissions_over_contact(contact),
        # Showing last 10 events by default
        'object': contact,
        'object_type': 'contacto',
        'starting_entry_number': 0,
        'history': contact.history(10, 0, user=request.user),
        'history_count': contact.history_count(user=request.user),
        'history_types': sorted({ccle.type for ccle in all_history}, key=lambda ccle: ccle.description),
        'users': sorted({ccle.user for ccle in all_history}, key=lambda user: user.full_name),
        # Showing last 10 events by default
        'contact_properties': contact.properties(user=request.user),
        'contact_properties_count': contact.properties_count(user=request.user),
        'property': property,
        'property_relationship_type': property_relationship_type,
        'countries': Country.objects.all(),
        'property_types': PropertyType.objects.all(),
        'property_common_attributes': common_attributes(),
        'default_name': {'first': first_name, 'last': last_name}
    }
    return HttpResponse(template.render(context, request))


@login_required
def contact_modal(request, contact_id, property_id=None):
    contact = Contact.objects.get(id=int(contact_id))
    relationship = ContactPropertyRelationship.objects\
        .filter(contact_id=int(contact_id), parent_property_id=int(property_id if property_id else 0)).first()
    relationship = relationship if relationship and \
                                   (not relationship.owner or
                                    request.user.permissions_over_property(relationship.parent_property)) else None

    if contact.company != request.user.company or (relationship and
                                                   relationship.parent_property.company != request.user.company):
        return HttpResponseForbidden()
    template = loader.get_template('collaborative_crm/contact_modal.html')
    context = {
        'contact': contact,
        'relationship': relationship,
        'can_edit': request.user.permissions_over_contact(contact)
    }
    return HttpResponse(template.render(context, request))


@login_required
def contact_history(request, contact_id, next_n_entries, starting_entry_number=1):
    if request.method == 'POST':
        contact = Contact.objects.get(id=int(contact_id))
        if contact.company != request.user.company:
            return HttpResponseForbidden()

        filters = dict((k, v) for k, v in json.loads(request.body).iteritems() if v)
        
        template = loader.get_template('collaborative_crm/history_data.html')
        context = {
            'object': contact,
            'object_type': 'contacto',
            'starting_entry_number': int(starting_entry_number) - 1,
            'history': contact.history(int(next_n_entries), int(starting_entry_number) - 1, filters=filters, 
                                       user=request.user),
            'history_count': contact.history_count(filters=filters, user=request.user)
        }

        return HttpResponse(template.render(context, request))

    return HttpResponseForbidden()


@login_required
def contact_history_details(request, contact_id, history_entry_id):
    contact = Contact.objects.get(id=int(contact_id))
    entry = contact.contactchangelogentry_set.get(id=int(history_entry_id))
    if contact.company != request.user.company or (entry.requires_permissions and
                                                   not request.user.permissions_over_contact(contact)):
        return HttpResponseForbidden()
    return HttpResponse(json.dumps(entry.to_dict), content_type='application/json')


@login_required
def contact_history_modal(request, contact_id, history_entry_id):
    contact = Contact.objects.get(id=int(contact_id))
    entry = contact.contactchangelogentry_set.get(id=int(history_entry_id))
    if contact.company != request.user.company or (entry.requires_permissions and
                                                   not request.user.permissions_over_contact(contact)):
        return HttpResponseForbidden()
    template = loader.get_template('collaborative_crm/history_modal.html')
    return HttpResponse(template.render({'entry': entry}, request))


@login_required
def contact_properties(request, contact_id, next_n_properties, starting_property_number):
    contact = Contact.objects.get(id=int(contact_id))
    if contact.company != request.user.company:
        return HttpResponseForbidden()
    return HttpResponse(
        json.dumps({
            'properties': [{
                'property': p['parent_property'].to_dict,
                'owner': p['parent_property'].owner.contact.to_dict if p['parent_property'].owner else None,
                'url': reverse('collaborative_crm:property', args=(p['parent_property'].id, )),
                'relationship_type': p['relationship_type'], 'commentary': p['commentary'],
                'last_modified_datetime': utc_to_local(p['last_modified_datetime']).strftime('%d/%m/%Y %H:%M:%S')
            } for p in contact.properties(int(next_n_properties), int(starting_property_number) - 1,
                                          user=request.user)],
            'total_properties_count': contact.properties_count(user=request.user)
        }), content_type='application/json')


@login_required
def contact_property(request, contact_id, property_id):
    contact = Contact.objects.get(id=int(contact_id))
    property = contact.property_data(property_id, user=request.user)
    if not property:
        return property_details(request, property_id)
    if contact.company != request.user.company or property['parent_property'].company != request.user.company:
        return HttpResponseForbidden()
    return HttpResponse(
        json.dumps({
            'property': property['parent_property'].to_dict,
            'owner': property['parent_property'].owner.contact.to_dict if property['parent_property'].owner else None,
            'url': reverse('collaborative_crm:property', args=(property['parent_property'].id, )),
            'relationship_type': property['relationship_type'],
            'commentary': property['commentary'],
            'last_modified_datetime': utc_to_local(property['last_modified_datetime']).strftime('%d/%m/%Y %H:%M:%S')
        }), content_type='application/json')


@login_required
@transaction.atomic
def contact_property_update(request, contact_id, property_id):
    if request.method == 'POST':
        try:
            parameters = json.loads(request.body)
            contact_property = ContactPropertyRelationship.objects.select_for_update()\
                .get(contact_id=int(contact_id), parent_property_id=int(property_id))
            if contact_property.contact.company != request.user.company or \
               contact_property.parent_property.company != request.user.company or \
                    (contact_property.owner and
                     not request.user.permissions_over_property(contact_property.parent_property)):
                return HttpResponseForbidden()
            contact_property.set_commentary(parameters['commentary'], logging_user=request.user)

            if contact_property.parent_property.user:
                contact_property.parent_property.user.notify(
                    'property_in_charge_changed', request.user,
                    data={'related_property_id': contact_property.parent_property.id}, request=request)
            if contact_property.contact.user:
                contact_property.contact.user.notify('contact_in_charge_changed', request.user,
                                                     data={'contact_id': contact_property.contact.id}, request=request)
            response = json.dumps({'status': 'Ok',
                                   'last_modified_datetime': utc_to_local(contact_property.last_modified_datetime)
                                  .strftime('%d/%m/%Y %H:%M:%S')})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
def contact_searches(request, contact_id, next_n_searches, starting_search_number):
    contact = Contact.objects.get(id=int(contact_id))
    if contact.company != request.user.company:
        return HttpResponseForbidden()
    searches = [s.to_dict() for s in contact.searches(int(next_n_searches), int(starting_search_number) - 1)]
    for search in searches:
        search['date'] = utc_to_local(search['date']).strftime('%d/%m/%Y')
    return HttpResponse(
        json.dumps({
            'searches': searches,
            'total_searches_count': contact.searches_count
        }), content_type='application/json')


@login_required
def contact_search(request, contact_id, search_id):
    contact = Contact.objects.get(id=int(contact_id))
    if contact.company != request.user.company:
        return HttpResponseForbidden()
    search = contact.contactsearch_set.get(id=int(search_id)).to_dict(elements_data=True)
    search['date'] = utc_to_local(search['date']).strftime('%d/%m/%Y')
    return HttpResponse(json.dumps(search), content_type='application/json')


@login_required
@transaction.atomic
def contact_search_update_commentary(request, contact_id, search_id):
    if request.method == 'POST':
        try:
            contact = Contact.objects.get(id=int(contact_id))
            if contact.company != request.user.company:
                return HttpResponseForbidden()
            search = contact.contactsearch_set.select_for_update().get(id=int(search_id))
            search.set_commentary(request.body, logging_user=request.user)
            if contact.user:
                contact.user.notify('contact_in_charge_changed', request.user, data={'contact_id': contact.id},
                                    request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})

        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def delete_contact_search(request, contact_id, search_id):
    if request.method == 'DELETE':
        try:
            contact = Contact.objects.get(id=int(contact_id))
            if contact.company != request.user.company:
                return HttpResponseForbidden()
            contact.contactsearch_set.select_for_update().get(id=int(search_id)).delete(logging_user=request.user)
            if contact.user:
                contact.user.notify('contact_in_charge_changed', request.user, data={'contact_id': contact.id},
                                    request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})

        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def create_contact(request, name=None):
    if request.method == 'POST' or (request.method == 'GET' and name):
        try:
            first_name = None
            last_name = None
            if name:
                first_name = name.split(' ', 1)[0]
                try:
                    last_name = name.split(' ', 1)[1]
                except IndexError:
                    pass
            if not name and (not request.POST.get('first-name') and not request.POST.get('email')):
                return HttpResponseForbidden()
            contact = Contact(company=request.user.company, user=request.user,
                              first_name=request.POST.get('first-name'), last_name=request.POST.get('last-name'),
                              telephone_number=request.POST.get('telephone-number'), email=request.POST.get('email'),
                              country_id=request.POST.get('country'), state_id=request.POST.get('state'),
                              city_id=request.POST.get('city'), neighborhood_id=request.POST.get('neighborhood'),
                              address=request.POST.get('address'), document=request.POST.get('document'),
                              works_at=request.POST.get('works-at'),
                              alternative_telephone_number=request.POST.get('alternative-telephone-number'),
                              alternative_email=request.POST.get('alternative-email')) \
                if not name else Contact(company=request.user.company, user=request.user, first_name=first_name,
                                         last_name=last_name)
            contact.save()
            ContactChangeLogEntry(change_type='creation', user=request.user, contact=contact).save()
            if not name:
                if request.POST.get('property-owner-id') or request.POST.get('property-interested-id'):
                    if request.POST.get('property-owner-id'):
                        field_name = 'property-owner-id'
                        type_desc = 'owner'
                    else:
                        field_name = 'property-interested-id'
                        type_desc = 'interested'
                    ContactPropertyRelationship(
                        parent_property=Property.objects.get(id=int(request.POST.get(field_name))), contact=contact,
                        type_desc=type_desc, logging_user=request.user).save()
            request.user.company.notify('contact_created', request.user, data={'contact_id': contact.id},
                                        request=request)
            return redirect('collaborative_crm:contact', 'contacto', contact.id)
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def update_contact_field(request, contact_id):
    if request.method == 'POST':
        try:
            contact = Contact.objects.select_for_update().get(id=int(contact_id))
            if contact.company != request.user.company or not request.user.permissions_over_contact(contact):
                return HttpResponseForbidden()
            parameters = json.loads(request.body)
            field_names_map = {
                'first-name': 'first_name',
                'last-name': 'last_name',
                'telephone-number': 'telephone_number',
                'email': 'email',
                'country': 'country_id',
                'state': 'state_id',
                'city': 'city_id',
                'neighborhood': 'neighborhood_id',
                'address': 'address',
                'document': 'document',
                'works-at': 'works_at',
                'alternative-telephone-number': 'alternative_telephone_number',
                'alternative-email': 'alternative_email'
            }
            field_proxy_class_map = {
                'country': {'class': 'Country', 'source_field': 'id', 'target_field': 'name'},
                'state': {'class': 'State', 'source_field': 'id', 'target_field': 'name'},
                'city': {'class': 'City', 'source_field': 'id', 'target_field': 'name'},
                'neighborhood': {'class': 'Neighborhood', 'source_field': 'id', 'target_field': 'name'}
            }
            change = False
            old_value = getattr(contact, field_names_map[parameters['fieldName']])
            if (old_value.__class__ != int and old_value != parameters['fieldValue']) or \
                    (old_value.__class__ == int and old_value != int(parameters['fieldValue'])):
                change = True
                setattr(contact, field_names_map[parameters['fieldName']], parameters['fieldValue'])
                change_log_entry = ContactChangeLogEntry(change_type='edition', user=request.user, contact=contact,
                                                         attribute=field_names_map[parameters['fieldName']],
                                                         old_value=old_value, new_value=parameters['fieldValue'])
                contact.save()
                if parameters['fieldName'] in field_proxy_class_map.keys():
                    change_log_entry.proxy_class = field_proxy_class_map[parameters['fieldName']]['class']
                    change_log_entry.proxy_source_field = field_proxy_class_map[parameters['fieldName']]['source_field']
                    change_log_entry.proxy_target_field = field_proxy_class_map[parameters['fieldName']]['target_field']
                change_log_entry.save()
                if contact.user:
                    contact.user.notify('contact_in_charge_changed', request.user, data={'contact_id': contact.id},
                                        request=request)
            response = json.dumps({'status': 'Ok', 'change': change})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def contact_assign_agent(request, contact_id, user_id=None):
    if request.method == 'POST':
        try:
            contact = Contact.objects.select_for_update().get(id=int(contact_id))
            user = User.objects.get(id=int(user_id)) if user_id else None

            # Fail any of the following occur:
            # 1) contact is from other company, 2) user to be assigned is from other company, 3) user is not oneself and
            # requesting user has no permission to assign other agents to contacts, 4) requesting user does not have
            # permissions over user currently assigned to contact, 5) requesting user does not have permissions over
            # user to be assigned to contact
            if contact.company != request.user.company or (user and user.company != request.user.company) or \
                    (user and not request.user.has_perm('collaborative_crm.contact_assign_agents') and
                     user != request.user) or \
                    (contact.user and not request.user.permissions_over_user(contact.user)) or \
                    (user and not request.user.permissions_over_user(user)):
                return HttpResponseForbidden()

            old_user = contact.user if not user and contact.user else None
            contact.set_user(user, logging_user=request.user)
            if user:
                user.notify('contact_assigned', request.user, data={'contact_id': contact.id}, request=request)
            elif old_user:
                old_user.notify('contact_unassigned', request.user, data={'contact_id': contact.id}, request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def contact_execute_state_action(request, contact_id, action_id):
    if request.method == 'POST':
        try:
            contact = Contact.objects.select_for_update().filter(company=request.user.company, id=int(contact_id))\
                .first()
            action = ContactWorkflowAction.objects.filter(source_state=contact.get_status if contact else None,
                                                          id=int(action_id)).first()
            if not contact or not action:
                return HttpResponseForbidden()

            contact.execute_status_action(action, logging_user=request.user)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def delete_contact(request, contact_id):
    if request.method == 'DELETE':
        try:
            contact = Contact.objects.select_for_update().get(id=int(contact_id))
            if contact.company != request.user.company:
                return HttpResponseForbidden()
            if contact.user:
                contact.user.notify('contact_in_charge_removed', request.user, data={'details': unicode(contact)},
                                    request=request)
            request.user.company.notify('contact_removed', request.user, data={'details': unicode(contact)},
                                        request=request)
            contact.delete()
            response = json.dumps({'status': 'Ok', 'redirect': reverse('collaborative_crm:contact',
                                                                       args=('nuevo_contacto', ))})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
def properties(request, my_properties):
    only_my_properties = my_properties == 'mis_propiedades'
    template = loader.get_template('collaborative_crm/properties.html')
    context = {
        'web_title': 'LinkedProp | {0}'.format('Propiedades' if not only_my_properties else 'Mis Propiedades'),
        'page_title': 'Propiedades' if not only_my_properties else 'Mis Propiedades',
        'page_sub_title': u'Propiedades de mi empresa' if not only_my_properties else u'Propiedades a mi cargo',
        'page_name': 'property',
        'my_properties': only_my_properties,
        'property_types': PropertyType.objects.all(),
        'property_common_attributes': common_attributes()
    }
    return HttpResponse(template.render(context, request))


@login_required
def property(request, property_id, contact_relationship_type=None, contact_id=None):
    template = loader.get_template('collaborative_crm/property.html')
    try:
        property = Property.objects.get(id=int(property_id))
    except Property.DoesNotExist:
        property = Property()
        property.id = 0

    if property.id != 0 and property.company != request.user.company:
        return HttpResponseForbidden()

    contact = None
    if contact_id:
        if property.id != 0:
            return redirect('collaborative_crm:property', property.id)
        else:
            contact = Contact.objects.get(id=int(contact_id))
            contact_relationship_type_map = {
                'dueno': 'owner',
                'interesado': 'interested'
            }
            contact_relationship_type = contact_relationship_type_map[contact_relationship_type]

    for notification in Notification.objects.filter(user=request.user, related_property=property, seen=False):
        notification.seen = True
        notification.save()

    all_history = property.propertychangelogentry_set.all()

    context = {
        'web_title': u'LinkedProp | Propiedad - {0}'.format(property) if property.id != 0
        else 'LinkedProp | Nueva propiedad',
        'page_title': u'{0}. {1}'.format(property.id, property) if property.id != 0 else 'Nueva propiedad',
        'page_sub_title': u'Página de propiedad',
        'page_name': 'property',
        'property': property,
        'can_edit': request.user.permissions_over_property(property),
        'property_types': PropertyType.objects.all(),
        'property_statuses': PropertyStatus.objects.all(),
        'countries': Country.objects.all(),
        # Showing last 10 events by default
        'object': property,
        'object_type': 'propiedad',
        'starting_entry_number': 0,
        'history': property.history(10, 0, user=request.user),
        'history_count': property.history_count(user=request.user),
        'history_types': sorted({pcle.type for pcle in all_history}, key=lambda pcle: pcle.description),
        'users': sorted({pcle.user for pcle in all_history}, key=lambda user: user.full_name),
        # Showing last 10 events by default
        # Showing latest 10 interested contacts by default
        'interested_contacts': property.interested_contacts(last_n_contacts=10),
        'contact': contact,
        'contact_relationship_type': contact_relationship_type,
        'open_images_modal': request.session.pop('images') if 'images' in request.session.keys() else None
    }
    return HttpResponse(template.render(context, request))


@login_required
def property_details(request, property_id):
    property = Property.objects.get(id=int(property_id))
    if property.company != request.user.company:
        return HttpResponseForbidden()
    return HttpResponse(json.dumps({'property': property.to_dict,
                                    'owner': property.owner.contact.to_dict if property.owner else None}),
                        content_type='application/json')


@login_required
def property_modal(request, property_id, contact_id=None):
    property = Property.objects.get(id=int(property_id))
    contact = Contact.objects.filter(id=int(contact_id if contact_id else 0)).first()
    if property.company != request.user.company or (contact and contact.company != request.user.company):
        return HttpResponseForbidden()
    template = loader.get_template('collaborative_crm/property_modal.html')
    contact_property_rel = ContactPropertyRelationship.objects.filter(contact=contact, parent_property=property).first()
    if contact_property_rel and contact_property_rel.owner and not request.user.permissions_over_property(property):
        contact = None
        contact_property_rel = None
    context = {
        'property': property,
        'contact': contact,
        'contact_property_rel': contact_property_rel,
        'can_edit': request.user.permissions_over_property(property)
    }
    return HttpResponse(template.render(context, request))


@login_required
def property_files_modal(request, property_id, selected_contact_id=None):
    property = Property.objects.get(id=int(property_id))
    selected_contact = Contact.objects.filter(id=int(selected_contact_id if selected_contact_id else 0)).first()
    if property.company != request.user.company or (selected_contact and
                                                    selected_contact.company != request.user.company):
        return HttpResponseForbidden()
    template = loader.get_template('collaborative_crm/file_modal.html')
    context = {
        'property': property,
        'selected_contact': selected_contact,
        'all_contacts_with_email': Contact.objects.filter(company=request.user.company).exclude(email='')
                                                                                       .exclude(email=None),
        'all_users_but_me': User.objects.filter(userextension__company=request.user.company).exclude(id=request.user.id)
    }
    return HttpResponse(template.render(context, request))


@login_required
def property_history(request, property_id, next_n_entries, starting_entry_number=1):
    if request.method == 'POST':
        property = Property.objects.get(id=int(property_id))
        if property.company != request.user.company:
            return HttpResponseForbidden()
        
        filters = dict((k, v) for k, v in json.loads(request.body).iteritems() if v)

        template = loader.get_template('collaborative_crm/history_data.html')
        context = {
            'object': property,
            'object_type': 'propiedad',
            'starting_entry_number': int(starting_entry_number) - 1,
            'history': property.history(int(next_n_entries), int(starting_entry_number) - 1, filters=filters,
                                        user=request.user),
            'history_count': property.history_count(filters=filters, user=request.user)
        }

        return HttpResponse(template.render(context, request))

    return HttpResponseForbidden()


@login_required
def property_history_details(request, property_id, history_entry_id):
    property = Property.objects.get(id=int(property_id))
    entry = property.propertychangelogentry_set.get(id=int(history_entry_id))
    if property.company != request.user.company or (entry.requires_permissions and
                                                    not request.user.permissions_over_property(property)):
        return HttpResponseForbidden()
    return HttpResponse(json.dumps(entry.to_dict), content_type='application/json')


@login_required
def property_history_modal(request, property_id, history_entry_id):
    property = Property.objects.get(id=int(property_id))
    entry = property.propertychangelogentry_set.get(id=int(history_entry_id))
    if property.company != request.user.company or (entry.requires_permissions and
                                                    not request.user.permissions_over_property(property)):
        return HttpResponseForbidden()
    template = loader.get_template('collaborative_crm/history_modal.html')
    return HttpResponse(template.render({'entry': entry}, request))


@login_required
@transaction.atomic
def create_property(request):
    if request.method == 'POST':
        try:
            if request.POST.get('street') is None or request.POST.get('street') == u'' or \
                            request.POST.get('number') is None or request.POST.get('number') == u'' or \
                            request.POST.get('city') is None or request.POST.get('city') in [u'', u'0', u'-1']:
                return HttpResponseForbidden()
            property = Property(company=request.user.company, user=request.user, type_id=request.POST.get('type'),
                                status=PropertyStatus.objects.get(name=Property.default_status_name),
                                city_id=request.POST.get('city'), neighborhood_id=request.POST.get('neighborhood'),
                                street=request.POST.get('street'), number=request.POST.get('number'),
                                floor=request.POST.get('floor'), apartment=request.POST.get('apartment'),
                                intersecting_street_1=request.POST.get('intersecting-street-1'),
                                intersecting_street_2=request.POST.get('intersecting-street-2'),
                                anonymous_address=request.POST.get('anonymous-address'),
                                description=request.POST.get('description'))

            if not property.anonymous_address:
                property.anonymous_address = property.generate_anonymous_address
            property.save()
            PropertyChangeLogEntry(change_type='creation', user=request.user, parent_property=property).save()
            if request.POST.get('owner-id') or request.POST.get('interested-contact-id'):
                if request.POST.get('owner-id'):
                    field_name = 'owner-id'
                    type_desc = 'owner'
                else:
                    field_name = 'interested-contact-id'
                    type_desc = 'interested'
                ContactPropertyRelationship(parent_property=property,
                                            contact=Contact.objects.get(id=int(request.POST.get(field_name))),
                                            type_desc=type_desc, logging_user=request.user).save()
            request.user.company.notify('property_created', request.user, data={'related_property_id': property.id},
                                        request=request)
            return redirect('collaborative_crm:property', property.id)
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def update_property_field(request, property_id):
    if request.method == 'POST':
        try:
            property = Property.objects.select_for_update().get(id=int(property_id))
            if property.company != request.user.company or not request.user.permissions_over_property(property):
                return HttpResponseForbidden()
            parameters = json.loads(request.body)
            field_names_map = {
                'type': 'type_id',
                'status': 'status_id',
                'city': 'city_id',
                'neighborhood': 'neighborhood_id',
                'street': 'street',
                'number': 'number',
                'floor': 'floor',
                'apartment': 'apartment',
                'intersecting-street-1': 'intersecting_street_1',
                'intersecting-street-2': 'intersecting_street_2',
                'anonymous-address': 'anonymous_address',
                'description': 'description',
                'for-sale': 'for_sale',
                'sale-price': 'sale_price',
                'sale-price-usd': 'sale_price_usd',
                'for-rent': 'for_rent',
                'rent-price': 'rent_price',
                'rent-price-usd': 'rent_price_usd'
            }
            field_proxy_class_map = {
                'type': {'class': 'PropertyType', 'source_field': 'id', 'target_field': 'description'},
                'status': {'class': 'PropertyStatus', 'source_field': 'id', 'target_field': 'name'},
                'city': {'class': 'City', 'source_field': 'id', 'target_field': 'name'},
                'neighborhood': {'class': 'Neighborhood', 'source_field': 'id', 'target_field': 'name'}
            }

            change = False
            old_value = getattr(property, field_names_map[parameters['fieldName']])
            if (old_value.__class__ != int and old_value != parameters['fieldValue']) or \
                    (old_value.__class__ == int and old_value != int(parameters['fieldValue'])):
                change = True
                setattr(property, field_names_map[parameters['fieldName']], parameters['fieldValue'])
                # Status is locked if property is either unavailable (neither for sale/rent) or pending appraisal info
                if parameters['fieldName'] == 'status':
                    property.check_status_consistency()
                change_log_entry = PropertyChangeLogEntry(change_type='edition', user=request.user,
                                                          parent_property=property,
                                                          attribute=field_names_map[parameters['fieldName']],
                                                          old_value=old_value, new_value=parameters['fieldValue'])
                property.save()
                if parameters['fieldName'] in field_proxy_class_map.keys():
                    change_log_entry.proxy_class = field_proxy_class_map[parameters['fieldName']]['class']
                    change_log_entry.proxy_source_field = field_proxy_class_map[parameters['fieldName']]['source_field']
                    change_log_entry.proxy_target_field = field_proxy_class_map[parameters['fieldName']]['target_field']
                change_log_entry.save()
                if property.user:
                    property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                               property.id},
                                         request=request)
            response = json.dumps({'status': 'Ok', 'change': change,
                                   'new_anonymous_address': property.generate_anonymous_address})
        except Property.PropertyStatusInconsistent:
            return HttpResponseForbidden()
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def attribute(request, property_id):
    if request.method == 'POST':
        try:
            property = Property.objects.select_for_update().get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            parameters = json.loads(request.body)
            if parameters['attribute'] in property.common_attributes_filed_map:
                old_value = getattr(property, parameters['attribute'])
                setattr(property, parameters['attribute'], parameters['value'] if parameters['value'] else None)
                property.save()
                PropertyChangeLogEntry(change_type='property_attribute_edition', user=request.user,
                                       parent_property=property, attribute=parameters['attribute'],
                                       new_value=getattr(property, parameters['attribute']), old_value=old_value).save()
            else:
                field_names_map = {
                    'value': 'value',
                    'unit-value': 'unit',
                    'numeric-attribute': 'format',
                    'unit-before': 'unit_prefix'
                }
                try:
                    attribute = property.propertyextraattribute_set.select_for_update()\
                        .get(description=parameters['attribute'])
                    old_value = attribute.formatted_value
                    setattr(attribute, field_names_map[parameters['attribute_field']],
                            parameters['value'] if parameters['value'] else None)
                    PropertyChangeLogEntry(change_type='property_attribute_edition', user=request.user,
                                           parent_property=property, attribute=parameters['attribute'],
                                           new_value=attribute.formatted_value, old_value=old_value).save()
                except PropertyExtraAttribute.DoesNotExist:
                    attribute = property.propertyextraattribute_set.create(description=parameters['attribute'])
                    PropertyChangeLogEntry(change_type='property_attribute_creation', user=request.user,
                                           parent_property=property, attribute=parameters['attribute']).save()
                attribute.save()
            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)

            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def delete_attribute(request, property_id):
    if request.method == 'DELETE':
        try:
            property = Property.objects.select_for_update().get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            property.propertyextraattribute_set.select_for_update().get(description=request.body).delete(
                logging_user=request.user)
            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
def property_image(request, property_id, image_id):
    property = Property.objects.get(id=int(property_id))
    if request.user.company != property.company:
        return HttpResponseForbidden()
    return HttpResponse(property.propertyimage_set.get(id=int(image_id)).image, content_type='image')


@login_required
@transaction.atomic
def property_upload_images(request, property_id):
    if request.method == 'POST':
        property = Property.objects.select_for_update().get(id=int(property_id))
        if request.user.company != property.company:
            return HttpResponseForbidden()
        property.propertyimage_set.add(PropertyImage(parent_property=property, image=request.FILES['file'],
                                                     logging_user=request.user))
        property.save()
        request.session['images'] = True
        if property.user:
            property.user.notify('property_in_charge_changed', request.user, data={'related_property_id': property.id},
                                 request=request)
        return HttpResponse(json.dumps({'status': 'Ok', 'redirect': reverse('collaborative_crm:property',
                                                                            args=(property.id, ))}),
                            content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def property_edit_image_description(request, property_id, image_id):
    if request.method == 'POST':
        try:
            property = Property.objects.get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            image = property.propertyimage_set.select_for_update().get(id=int(image_id))
            image.set_description(request.body, logging_user=request.user)
            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def property_set_cover_image(request, property_id, image_id):
    if request.method == 'POST':
        try:
            property = Property.objects.get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            image = property.propertyimage_set.select_for_update().get(id=int(image_id))
            property.set_cover_image(image, logging_user=request.user)
            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def property_delete_image(request, property_id, image_id):
    if request.method == 'DELETE':
        try:
            property = Property.objects.get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            property.propertyimage_set.select_for_update().get(id=int(image_id)).delete(logging_user=request.user)
            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def property_assign_agent(request, property_id, user_id=None):
    if request.method == 'POST':
        try:
            property = Property.objects.select_for_update().get(id=int(property_id))
            user = User.objects.get(id=int(user_id)) if user_id else None
            # Fail any of the following occur:
            # 1) property is from other company, 2) user to be assigned is from other company, 3) user is not oneself
            # and requesting user has no permission to assign other agents to properties, 4) requesting user does not
            # have permissions over user currently assigned to property, 5) requesting user does not have permissions
            # over user to be assigned to property
            if property.company != request.user.company or (user and user.company != request.user.company) or \
                    (user and not request.user.has_perm('collaborative_crm.property_assign_agents') and
                     user != request.user) or \
                    (property.user and not request.user.permissions_over_user(property.user)) or \
                    (user and not request.user.permissions_over_user(user)):
                return HttpResponseForbidden()
            old_user = property.user if not user and property.user else None
            property.set_user(user, logging_user=request.user)
            if user:
                user.notify('property_assigned', request.user, data={'related_property_id': property.id},
                            request=request)
            elif old_user:
                old_user.notify('property_unassigned', request.user, data={'related_property_id': property.id},
                                request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


def get_file_temp_name_from_attributes(property, file_type, attributes):
    return property.get_file(file_type, hide_exact_address='ocultar-direccion-exacta' in attributes,
                             include_images='no-incluir-imagenes' not in attributes,
                             include_cover_image='no-incluir-imagen-portada' not in attributes)


@login_required
def property_file_download(request, property_id, file_type, attributes='', file_name=None, file_extension=None):
    if request.method == 'GET':
        property = Property.objects.get(id=int(property_id))
        if property.company != request.user.company:
            return HttpResponseForbidden()
        file_temp_name = get_file_temp_name_from_attributes(property, file_type, attributes)
        file_content = open(file_temp_name, 'rb').read()
        shutil.rmtree(os.path.dirname(file_temp_name))
        response = HttpResponse(file_content,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                if file_type == 'excel' else 'application/force-download')
        return response

    return HttpResponseForbidden()


@login_required
def property_file_send_email(request, property_id, file_type, attributes=''):
    if request.method == 'POST':
        try:
            property = Property.objects.get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            parameters = json.loads(request.body)
            recipient_list = \
                [c for c in Contact.objects.filter(company=request.user.company,
                                                   id__in=parameters.get('contacts_to', [])) if c.email] + \
                [u for u in User.objects.filter(userextension__company=request.user.company,
                                                id__in=parameters.get('users_to', []))] + \
                [request.user] if parameters.get('send_to_myself') else []

            file_temp_name = get_file_temp_name_from_attributes(property, file_type, attributes)
            template = loader.get_template('collaborative_crm/email_property_file.html')
            template_plain = loader.get_template('collaborative_crm/email_property_file.txt')

            for recipient in recipient_list:
                recipient_type = 'contact' if recipient.__class__.__name__ == 'Contact' else 'user'
                context = {
                    'property': property,
                    'request_user': request.user,
                    'recipient': recipient,
                    'recipient_type': recipient_type,
                    'link_to_property': request.build_absolute_uri(reverse('collaborative_crm:property',
                                                                           args=(property.id, ))),
                    'message': parameters.get('message'),
                    'email': request.user.username if parameters.get('include_email') else None,
                    'telephone_number': request.user.telephone_number if parameters.get('include_telephone_number')
                    else None,
                    'linked_prop_email': linked_prop_email,
                    'linked_prop_telephone': linked_prop_telephone
                }
                create_html_plain_email(u'{0}Ficha de propiedad {1}'.format(
                    u'[LinkedProp] ' if recipient_type == 'user' else u'',
                    property.anonymous_address if property.anonymous_address else property),
                    template_plain.render(context, request), template.render(context, request),
                    [recipient.email if recipient_type == 'contact' else recipient.username],
                    attachments_paths=[{'file_path': file_temp_name,
                                        'mime_type': 'application/vnd.openxmlformats-'
                                                     'officedocument.spreadsheetml.sheet'}]).send()
            shutil.rmtree(os.path.dirname(file_temp_name))
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def delete_property(request, property_id):
    if request.method == 'DELETE':
        try:
            property = Property.objects.select_for_update().get(id=int(property_id))
            if property.company != request.user.company:
                return HttpResponseForbidden()
            if property.user:
                property.user.notify('property_in_charge_removed', request.user, data={'details': unicode(property)},
                                     request=request)
            request.user.company.notify('property_removed', request.user, data={'details': unicode(property)},
                                        request=request)
            property.delete()
            response = json.dumps({'status': 'Ok', 'redirect': reverse('collaborative_crm:property', args=(0, ))})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def contact_property_create_relationship(request, contact_id, property_id, contact_property_relationship_type):
    if request.method == 'POST':
        try:
            contact = Contact.objects.get(id=int(contact_id))
            property = Property.objects.get(id=int(property_id))
            if contact.company != request.user.company or property.company != request.user.company or \
                    (contact_property_relationship_type == 'dueno' and
                     not request.user.permissions_over_property(property)):
                return HttpResponseForbidden()
            if contact_property_relationship_type == 'dueno':
                contact_property_relationship_type = 'owner'
                if ContactPropertyRelationship.objects.select_for_update().filter(
                        parent_property=property, type=ContactPropertyRelationshipType.objects.get(
                            description=ContactPropertyRelationship.type_owner_description)):
                    # Fail if property already has owner assigned
                    return HttpResponseForbidden()
            elif contact_property_relationship_type == 'interesado':
                contact_property_relationship_type = 'interested'
            for relationship in ContactPropertyRelationship.objects.filter(parent_property=property, contact=contact):
                if relationship.type.description == ContactPropertyRelationship.type_owner_description:
                    # Fails if contact is already assigned as owner. If assigned as interested, that relationship is
                    # deleted and the new one is created
                    return HttpResponseForbidden()
                relationship.select_for_update().delete(logging_user=request.user)
            ContactPropertyRelationship(parent_property=property, contact=contact, logging_user=request.user,
                                        type_desc=contact_property_relationship_type, commentary=request.body).save()
            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)
            if contact.user:
                contact.user.notify('contact_in_charge_changed', request.user, data={'contact_id': contact.id},
                                    request=request)

            response = json.dumps({'status': 'Ok', 'property': {'property': property.to_dict,
                                                                'commentary': request.body,
                                                                'relationship_type':
                                                                    u'Dueño'
                                                                    if contact_property_relationship_type == 'owner'
                                                                    else u'Interesado'}})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def contact_property_destroy_relationship(request, contact_id, property_id):
    if request.method == 'DELETE':
        try:
            contact = Contact.objects.get(id=int(contact_id))
            property = Property.objects.get(id=int(property_id))
            if contact.company != request.user.company or property.company != request.user.company:
                return HttpResponseForbidden()

            relationships = ContactPropertyRelationship.objects.filter(parent_property=property, contact=contact)
            if not request.user.permissions_over_property(property) and [r for r in relationships if r.owner]:
                return HttpResponseForbidden()

            for relationship in relationships:
                relationship.delete(logging_user=request.user)

            if property.user:
                property.user.notify('property_in_charge_changed', request.user, data={'related_property_id':
                                                                                       property.id},
                                     request=request)
            if contact.user:
                contact.user.notify('contact_in_charge_changed', request.user, data={'contact_id': contact.id},
                                    request=request)
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def notification_seen(request, notification_id=None):
    if request.method == 'POST':
        try:
            kwargs = {'user': request.user}
            if notification_id:
                kwargs['id'] = int(notification_id)
            notifications_list = Notification.objects.filter(**kwargs)
            if len(notifications_list) == 0:
                return HttpResponseForbidden()
            for notification in notifications_list:
                notification.seen = True
                notification.save()
            response = json.dumps({'status': 'Ok', 'unseen_notifications_count': len(request.user.unseen_notifications),
                                   'url': notifications_list[0].data['url'] if len(notifications_list) == 1 else None})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


def perform_search(request, entity_types, search_term, top_n_results):
    if len([c for c in search_term.strip().lower() if c in 'abcdefghijklmnopqrstuvwxyz0123456789']) <= 1:
        return []
    else:
        contact_q = reduce(
            lambda base_q, filt:
            base_q & reduce(lambda q, f: q | Q(**{'{0}{1}'.format(f, Contact.text_search_operation): filt}),
                            Contact.text_search_relevant_fields, Q()), search_term.strip().split(), Q())

        property_q = reduce(
            lambda base_q, filt:
            base_q & reduce(lambda q, f: q | Q(**{'{0}{1}'.format(f, Property.text_search_operation): filt}),
                            Property.text_search_relevant_fields, Q()), search_term.strip().split(), Q())

        user_q = reduce(
            lambda base_q, filt:
            base_q & reduce(lambda q, f: q | Q(**{'{0}{1}'.format(f, User.text_search_operation): filt}),
                            User.text_search_relevant_fields, Q()), search_term.strip().split(), Q())

        return \
            list(Contact.objects.filter(Q(company=request.user.company), contact_q)[:top_n_results]
                 if 'contactos' in entity_types else []) + \
            list(Property.objects.filter(Q(company=request.user.company), property_q)[:top_n_results]
                 if 'propiedades' in entity_types else []) + \
            ([u for u in
             list(User.objects.filter(Q(userextension__company=request.user.company), user_q)[:top_n_results])
             if not 'agentes-a-cargo' in entity_types or request.user.permissions_over_user(u)]\
                if 'agentes' in entity_types else [])


@login_required
def search(request, entity_types, search_term, top_n_results=6, starting_result=0):
    if request.method == 'GET':
        class_type_map = {
            Contact: 'contact',
            Property: 'property',
            User: 'user'
        }
        starting_result = int(starting_result) if starting_result else None
        top_n_results = int(top_n_results) if top_n_results else None
        response = sorted([{'id': o.id, 'type': class_type_map[o.__class__],
                            'image_url': o.cover_image.image_url if o.__class__ == Property and o.cover_image else None,
                            'full_name': o.full_name_with_text_search_matches(search_term),
                            'email': o.email_with_text_search_matches(search_term) if o.__class__ in [Contact, User]
                            else None, 'url': o.url if o.__class__ in [Contact, Property] else None,
                            'score': o.text_search_score(search_term)}
                           for o in perform_search(request, entity_types, search_term, top_n_results)],
                          key=lambda r: r['score'], reverse=True)[starting_result:top_n_results]

        return HttpResponse(json.dumps(response), content_type='application/json')

    return HttpResponseForbidden()


@login_required
def search_html(request, entity_types, search_term, top_n_results=6, starting_result=0):
    if request.method == 'GET':
        starting_result = int(starting_result) if starting_result else None
        top_n_results = int(top_n_results) if top_n_results else None
        template = loader.get_template('collaborative_crm/search_results.html')
        context = {
            'search_term': search_term,
            'results': sorted(perform_search(request, entity_types, search_term, top_n_results),
                              key=lambda r: r.text_search_score(search_term), reverse=True)
            [starting_result:top_n_results]
        }

        return HttpResponse(template.render(context, request))

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def search_contacts(request, top_n=100):
    if request.method == 'POST':
        template = loader.get_template('collaborative_crm/contacts_data.html')
        parameters = json.loads(request.body if request.body else '{}')

        if len(parameters.get('search_term', '').strip()) > 1:
            contacts = perform_search(request, entity_types='contactos', search_term=parameters['search_term'],
                                      top_n_results=top_n)
            if parameters.get('my_contacts', None):
                contacts = [c for c in contacts if c.user == request.user]
        else:
            filts = {'company': request.user.company}
            if parameters.get('my_contacts', None):
                filts['user'] = request.user
            contacts = Contact.objects.filter(**filts)[:top_n]

        return HttpResponse(template.render({'contacts': contacts}, request))

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def search_properties(request, contact_id=None, search_id=None):
    if request.method == 'POST':
        template = loader.get_template('collaborative_crm/properties_data.html')
        parameters = json.loads(request.body)
        user_param = [p for p in parameters['parameters'] if p['attribute'] == 'user_id' and p['values'] == 'me']
        if user_param:
            user_param[0]['values'] = request.user.id
        try:
            contact = Contact.objects.get(id=int(contact_id if contact_id else 0))
        except Contact.DoesNotExist:
            contact = None

        if contact and contact.company != request.user.company:
            return HttpResponseForbidden()
        if search_id:
            search = contact.contactsearch_set.select_for_update().get(id=int(search_id))
            search.commentary = parameters.get('commentary')
            if not parameters.get('useSearchParameters'):
                search.date = timezone.now()
                for elem in search.contactsearchelement_set.all():
                    elem.delete()
        else:
            search = ContactSearch(contact=contact, user=request.user, commentary=parameters.get('commentary'))
            if contact:
                search.save(log_event='contact_search_creation', logging_user=request.user)
            else:
                search.save()

        if not parameters.get('useSearchParameters'):
            for parameter in [p for p in parameters['parameters'] if 'values' in p.keys() and p['values']]:
                search.contactsearchelement_set.create(attribute=parameter['attribute'],
                                                       operation=parameter['operation'],
                                                       values=json.dumps(parameter['values']
                                                                         if not parameter['boolean']
                                                                         else parameter['values'] == 'yes'))
            if contact:
                if search_id and parameters.get('parametersChanged'):
                    search.save(log_event='contact_search_parameters_edition', logging_user=request.user)
                    if contact.user:
                        contact.user.notify('contact_in_charge_changed', request.user, data={'contact_id': contact.id},
                                            request=request)
            else:
                search_results = search.results
                search.delete()
                search = None

        return HttpResponse(template.render({'search': search,
                                             'search_results': search.results if search else search_results}, request))

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_config')
def my_company_config(request):
    template = loader.get_template('collaborative_crm/my_company_config.html')
    company = request.user.company
    context = {
        'web_title': u'LinkedProp | {0} | Mi empresa - Configuración'.format(company.name),
        'page_title': u'{0}'.format(company.name),
        'page_sub_title': u'Configuración',
        'page_name': 'my_company',
        'company': company,
        'notification_types': NotificationType.objects.all().order_by('order_index', 'id'),
        'user_groups': Group.objects.all(),
        'privacy_configs': CompanyPrivacyConfig.objects.all().order_by('order_index')
    }
    return HttpResponse(template.render(context, request))


@login_required
@permission_required('collaborative_crm.config_notifications')
def group_notifications_config(request, group_id):
    if request.method == 'GET':
        return HttpResponse(json.dumps({
            'status': 'Ok',
            'configs': [gnc.to_dict for gnc in GroupNotificationConfig.objects.filter(company=request.user.company,
                                                                                      group_id=int(group_id))]
        }), content_type='application/json')

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.config_notifications')
@transaction.atomic
def update_group_notifications_config(request, group_id):
    if request.method == 'POST':
        for notification_type_id in notification_types.values():
            overwrite_user_configs = False
            try:
                gnf = GroupNotificationConfig.objects.get(company=request.user.company, group_id=int(group_id),
                                                          notification_type_id=notification_type_id)
            except GroupNotificationConfig.DoesNotExist:
                overwrite_user_configs = True
                gnf = GroupNotificationConfig(company=request.user.company, group_id=int(group_id),
                                              notification_type_id=notification_type_id)

            new_notify_value = request.POST.get('{0}-notify'.format(notification_type_id), False)
            new_email_value = request.POST.get('{0}-email'.format(notification_type_id), False)

            # if group configuration is not can_edit and something changed, then the user configs for that group and
            # notification type must be overwritten
            overwrite_user_configs |= (request.POST.get('{0}-edit-view'.format(notification_type_id)) != 'can_edit' and
                                       (gnf.notify != new_notify_value or gnf.email != new_email_value))

            gnf.notify = new_notify_value
            gnf.email = new_email_value
            if not gnf.group.is_admin:
                gnf.can_view = request.POST.get('{0}-edit-view'.format(notification_type_id)) \
                               in ['can_edit', 'can_view']
                gnf.can_edit = request.POST.get('{0}-edit-view'.format(notification_type_id)) == 'can_edit'
            gnf.save(overwrite_user_configs=overwrite_user_configs)

        return redirect('collaborative_crm:my_company_config')

    return HttpResponseForbidden()


@login_required
def company_logo(request, company_id):
    if request.user.company.id != int(company_id):
        return HttpResponseForbidden()
    return HttpResponse(Company.objects.get(id=int(company_id)).logo, content_type='image')


@login_required
@transaction.atomic
@permission_required('collaborative_crm.edit_config')
def company_update_data(request, company_id):
    if request.method == 'POST':
        if request.user.company.id != int(company_id):
            return HttpResponseForbidden()
        company = Company.objects.select_for_update().get(id=int(company_id))
        company.name = request.POST.get('name')
        company.save()
        return redirect('collaborative_crm:my_company_config')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
@permission_required('collaborative_crm.edit_config')
def company_update_logo(request, company_id):
    if request.method == 'POST':
        if request.user.company.id != int(company_id):
            return HttpResponseForbidden()
        company = Company.objects.select_for_update().get(id=int(company_id))
        company.update_logo(request.FILES['file'])
        company.save()
        return HttpResponse(json.dumps({'status': 'Ok'}), content_type='application/json')

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_config')
def my_company_update_permissions(request):
    if request.method == 'POST':
        company = request.user.company
        company.privacy_config_id = int(request.POST.get('permissions-config', CompanyPrivacyConfig.none().id))
        company.super_agents_can_edit_config = request.POST.get('edit-config', False)
        company.super_agents_can_config_notifications = request.POST.get('config-notifications', False) and \
                                                        request.POST.get('edit-config', False)
        company.super_agents_can_edit_branches = request.POST.get('edit-branches', False)
        company.super_agents_can_edit_agents = request.POST.get('edit-agents', False)
        company.super_agents_can_assign_user_to_properties = request.POST.get('property-assign-agents', False)
        company.super_agents_can_assign_user_to_contacts = request.POST.get('contact-assign-agents', False)
        company.save()
        company.set_all_user_permissions()
        return redirect('collaborative_crm:my_company_config')

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_workflows')
def save_workflow(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                workflow_data = json.loads(request.body)
                workflow = ContactWorkflow.objects.select_for_update().filter(company=request.user.company,
                                                                              id=workflow_data['id']).first()
                if not workflow:
                    workflow = ContactWorkflow(company=request.user.company)
                workflow.name = workflow_data['name']
                workflow.description = workflow_data['description']

                workflow.save()

                for state in [st for st in workflow.states if st.id not in [s['id'] for s in workflow_data['states']]]:
                    print state
                    state.delete()

                states = {}
                for workflow_state in workflow_data['states']:
                    state = ContactWorkflowState.objects.filter(workflow=workflow, id=workflow_state['id']).first()
                    if not state:
                        state = ContactWorkflowState(workflow=workflow)
                    state.name = workflow_state['text']
                    state.position = workflow_state['position']
                    state.color = workflow_state['color']
                    state.save()

                    states[workflow_state['id']] = state

                def upsert_action(action_data, inverse=False):
                    action = ContactWorkflowAction.objects.filter(source_state=states[action_data['sourceStateId']],
                                                                  target_state=states[action_data['targetStateId']])\
                        .first()
                    if not action:
                        action = ContactWorkflowAction(source_state=states[action_data['sourceStateId']],
                                                       target_state=states[action_data['targetStateId']])

                    action.name = action_data['text']
                    automatic_data = action_data['automatic']
                    action.automatic_time = automatic_data['time'] if automatic_data else None
                    action.automatic_unit = automatic_data['unit'] if automatic_data else None
                    action.automatic_unlink_agent = automatic_data['unlinkAgent'] if automatic_data else False
                    action.automatic_notify = automatic_data['notify'] if automatic_data else False
                    action.automatic_email = automatic_data['email'] if automatic_data else False

                    action.is_inverse = inverse
                    action.save()

                actions = []
                for workflow_action in workflow_data['links']:
                    actions.append('{0}-{1}'.format(states[workflow_action['sourceStateId']].id,
                                                    states[workflow_action['targetStateId']].id))
                    upsert_action(workflow_action)
                    if workflow_action['inverse']:
                        actions.append('{0}-{1}'.format(states[workflow_action['targetStateId']].id,
                                                        states[workflow_action['sourceStateId']].id))
                        upsert_action(merge_two_dicts(workflow_action['inverse'],
                                                      {'sourceStateId': workflow_action['targetStateId'],
                                                       'targetStateId': workflow_action['sourceStateId']}),
                                      inverse=True)

                print actions
                print ['{0}-{1}'.format(a.source_state.id, a.target_state.id) for a in workflow.actions]
                print [a for a in workflow.actions if '{0}-{1}'.format(a.source_state.id, a.target_state.id) not in actions]

                for action in [a for a in workflow.actions
                               if '{0}-{1}'.format(a.source_state.id, a.target_state.id) not in actions]:
                    action.delete()

                if workflow.has_isolated_states:
                    response = json.dumps({'status': 'Error', 'error_message': u'El workflow tiene estados aislados '
                                                                               u'(bordes rojos). Todos los estados '
                                                                               u'deben estar comunicados con al menos '
                                                                               u'otro estado a través de, al menos, '
                                                                               u'una acción.'})
                    raise IntegrityError
                if workflow.has_no_initial_state:
                    response = json.dumps({'status': 'Error', 'error_message': u'El workflow no tiene estado inicial '
                                                                               u'(bordes verdes). Debe ser un estado '
                                                                               u'sin ninguna acción que dirija a el.'})
                    raise IntegrityError
                if workflow.has_many_initial_states:
                    response = json.dumps({'status': 'Error', 'error_message': u'El workflow tiene más de un estado '
                                                                               u'inicial (bordes verdes). Sólo puede '
                                                                               u'haber uno.'})
                    raise IntegrityError

                if workflow_data['isActive']:
                    workflow.set_active()

                response = json.dumps({'status': 'Ok'})
        except IntegrityError, e:
            pass
        except Exception, e:
            response = json.dumps({'status': 'Error', 'error_message': u'Error desconocido {0} - {1}'
                                  .format(str(e.__class__), str(e.message) if e.message is not None else '')})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
def workflow_details(request, workflow_id):
    workflow = ContactWorkflow.objects.filter(company=request.user.company, id=int(workflow_id)).first()
    if not workflow:
        return HttpResponseForbidden()
    return HttpResponse(json.dumps(workflow.to_dict(workflow_canvas_fields=True)), content_type='application/json')


@login_required
@permission_required('collaborative_crm.edit_workflows')
@transaction.atomic
def delete_workflow(request, workflow_id):
    if request.method == 'DELETE':
        try:
            workflow = ContactWorkflow.objects.select_for_update().filter(company=request.user.company,
                                                                          id=int(workflow_id), is_default=False).first()
            if not workflow:
                return HttpResponseForbidden()
            workflow.delete()
            response = json.dumps({'status': 'Ok'})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_branches')
def my_company_branches(request, selected_branch_id=0):
    template = loader.get_template('collaborative_crm/my_company_branches.html')
    company = request.user.company
    try:
        selected_branch = Branch.objects.get(id=int(selected_branch_id))
    except Branch.DoesNotExist:
        selected_branch = None
    if not selected_branch or selected_branch.company != company:
        selected_branch = Branch(company=company, id=0, name='')
    context = {
        'web_title': u'LinkedProp | {0} | Mi empresa - Sucursales'.format(company.name),
        'page_title': u'{0}'.format(company.name),
        'page_sub_title': u'Sucursales',
        'page_name': 'my_company',
        'company': company,
        'selected_branch': selected_branch,
        'countries': Country.objects.all()
    }
    return HttpResponse(template.render(context, request))


@login_required
@transaction.atomic
@permission_required('collaborative_crm.edit_branches')
def branch_update_data(request, company_id, branch_id):
    if request.method == 'POST':
        company = Company.objects.get(id=int(company_id))
        if company != request.user.company:
            return HttpResponseForbidden()
        try:
            branch = company.branch_set.select_for_update().get(id=int(branch_id))
            branch.code = request.POST.get('code')
            branch.name = request.POST.get('name', '')
            branch.city_id = request.POST.get('city')
            branch.address = request.POST.get('address')
            branch.description = request.POST.get('description')
        except Branch.DoesNotExist:
            branch = company.branch_set.create(code=request.POST.get('code'), name=request.POST.get('name', ''),
                                               city_id=request.POST.get('city'), address=request.POST.get('address'),
                                               description=request.POST.get('description'))
        branch.save()
        return redirect('collaborative_crm:my_company_branches', branch.id)

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_branches')
def branch_details(request, company_id, branch_id):
    branch = Branch.objects.get(id=int(branch_id))
    if int(company_id) != request.user.company.id or branch.company.id != int(company_id):
        return HttpResponseForbidden()
    return HttpResponse(json.dumps(branch.to_dict), content_type='application/json')


@login_required
@transaction.atomic
@permission_required('collaborative_crm.edit_branches')
def delete_branch(request, company_id, branch_id):
    if request.method == 'DELETE':
        company = Company.objects.get(id=int(company_id))
        if company != request.user.company:
            return HttpResponseForbidden()
        try:
            company.branch_set.select_for_update().get(id=int(branch_id)).delete()
            return HttpResponse(json.dumps({'status': 'Ok',
                                            'redirect': reverse('collaborative_crm:my_company_branches')}),
                                content_type='application/json')
        except Branch.DoesNotExist:
            return HttpResponseForbidden()

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_agents')
def my_company_agents(request):
    template = loader.get_template('collaborative_crm/my_company_agents.html')
    company = request.user.company
    context = {
        'web_title': u'LinkedProp | {0} | Mi empresa - Agentes'.format(company.name),
        'page_title': u'{0}'.format(company.name),
        'page_sub_title': u'Agentes',
        'page_name': 'my_company',
        'company': company,
        'groups': sorted([g for g in Group.objects.all() if not g.is_admin and
                          (not g.is_super_agent or request.user.is_admin)], key=lambda group: group.name)
    }
    return HttpResponse(template.render(context, request))


@login_required
@permission_required('collaborative_crm.edit_agents')
@transaction.atomic
def user_update_data(request, company_id, user_id):
    if request.method == 'POST':
        company = Company.objects.get(id=int(company_id))
        if company != request.user.company:
            return HttpResponseForbidden()
        try:
            user = User.objects.select_for_update().get(userextension__company=request.user.company, id=int(user_id))
            if user.username != request.POST.get('email', '') or user.is_admin or \
                    (request.user.is_super_agent and
                     (user.is_super_agent or not request.user.permissiosn_over_user(user))):
                return HttpResponseForbidden()
            user.first_name = request.POST.get('first-name')
            user.last_name = request.POST.get('last-name')
            user.save()
            if request.user.is_admin:
                user.groups.clear()
                user.groups.add(Group.objects.get(id=int(request.POST.get('type'))))
            user.userextension.telephone_number = request.POST.get('telephone-number')
            user.userextension.add_new_users_to_my_charge = request.POST.get('add-new-users-to-my-charge', False)
            user.userextension.add_my_branch_users_to_my_charge = request.POST.get('add-my-branch-users-to-my-charge',
                                                                                   False)
            user.userextension.save()
        except User.DoesNotExist:
            if request.POST.get('email', '') in [u.username for u in User.objects.all()]:
                return HttpResponseForbidden()
            user = User(username=request.POST.get('email', ''), first_name=request.POST.get('first-name'),
                        last_name=request.POST.get('last-name'), email=request.POST.get('email', ''))
            new_password = user.generate_random_password()
            send_welcome_email(request, user, new_password)
            user.set_password(new_password)
            user.save()
            if request.user.is_super_agent:
                user.groups.add(Group.objects.get(name='Agente'))
                request.user.add_user_in_charge(user)
            else:
                user.groups.add(Group.objects.get(id=int(request.POST.get('type'))))
            request.user.company.created_user(user)
            UserExtension(user=user, company=company, telephone_number=request.POST.get('telephone-number'),
                          add_new_users_to_my_charge=request.POST.get('add-new-users-to-my-charge', False),
                          add_my_branch_users_to_my_charge = request.POST.get('add-my-branch-users-to-my-charge',
                                                                              False)).save()

        user.set_main_branch(request.POST.get('main-branch'))
        user.set_users_in_charge(User.objects.filter(
            id__in=[int(uid) for uid in request.POST.getlist('users-in-charge', [])]))
        company.set_user_permissions(user)
        return redirect('collaborative_crm:my_company_agents')

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_agents')
def user_details(request, company_id, user_id):
    user = User.objects.get(id=int(user_id))
    if int(company_id) != request.user.company.id or user.company.id != int(company_id):
        return HttpResponseForbidden()
    return HttpResponse(json.dumps(user.to_dict), content_type='application/json')


@login_required
@permission_required('collaborative_crm.edit_agents')
@transaction.atomic
def user_reset_password(request, company_id, user_id):
    if request.method == 'POST':
        company = Company.objects.get(id=int(company_id))
        if company != request.user.company:
            return HttpResponseForbidden()
        try:
            user = User.objects.select_for_update().get(id=int(user_id))
            if user.company != company or user.is_admin or \
                    (request.user.is_super_agent and
                     (user.is_super_agent or not request.user.permissiosn_over_user(user))):
                return HttpResponseForbidden()
            new_password = user.generate_random_password()
            user.set_password(new_password)
            user.save()
            return HttpResponse(json.dumps({'status': 'Ok', 'new_password': new_password}),
                                content_type='application/json')
        except User.DoesNotExist:
            return HttpResponseForbidden()

    return HttpResponseForbidden()


@login_required
@permission_required('collaborative_crm.edit_agents')
@transaction.atomic
def delete_user(request, company_id, user_id):
    if request.method == 'DELETE':
        company = Company.objects.get(id=int(company_id))
        if company != request.user.company:
            return HttpResponseForbidden()
        try:
            user = User.objects.select_for_update().get(id=int(user_id))
            if user.company != company or user.is_admin:
                return HttpResponseForbidden()
            user.delete()
            return HttpResponse(json.dumps({'status': 'Ok',
                                            'redirect': reverse('collaborative_crm:my_company_agents')}),
                                content_type='application/json')
        except User.DoesNotExist:
            return HttpResponseForbidden()

    return HttpResponseForbidden()


@login_required
def messages(request, selected_conversation_id=None):
    selected_conversation = request.user.conversations(first=True, filters={'id': int(selected_conversation_id
                                                                                      if selected_conversation_id
                                                                                      else 0)})
    selected_conversation.user_read_all_messages(request.user)
    template = loader.get_template('collaborative_crm/messages.html')
    context = {
        'web_title': 'LinkedProp | Mensajes',
        'page_title': u'Mensajes',
        'page_sub_title': u'Chat con otros usuarios de {0}'.format(request.user.company.name),
        'page_name': 'messages',
        'conversations': sorted(request.user.conversations(), key=lambda conv: conv.latest_activity, reverse=True),
        'selected_conversation': selected_conversation,
        'all_users_but_me': User.objects.filter(userextension__company=request.user.company).exclude(id=request.user.id)
    }
    return HttpResponse(template.render(context, request))


@login_required
def create_conversation(request):
    if request.method == 'POST':
        try:
            parameters = json.loads(request.body)
            if not parameters.get('users'):
                return HttpResponseForbidden()
            users = User.objects.filter(userextension__company=request.user.company,
                                        id__in=[int(uid) for uid in parameters['users']] + [request.user.id])
            conversation = Conversation(title=parameters.get('title'), users=users)
            conversation.save()
            conversation_dict = conversation.to_dict
            conversation_dict['users_names_list'] = reduce(lambda nl, n: nl + u' | ' + n.full_name,
                                                           [u for u in conversation.users.all()
                                                            if u != request.user],
                                                           u'Yo')
            response = json.dumps({'status': 'Ok', 'conversation': conversation_dict})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
def conversation_messages(request, conversation_id, read_meesages=False):
    if request.method == 'GET':
        conversation = Conversation.objects.get(id=int(conversation_id))
        if not conversation.users.filter(id=request.user.id):
            return HttpResponseForbidden()
        if read_meesages:
            conversation.user_read_all_messages(request.user)
        template = loader.get_template('collaborative_crm/chat_data.html')
        context = {
            'conversation': conversation
        }
        return HttpResponse(template.render(context, request))

    return HttpResponseForbidden()


@login_required
def send_message(request, conversation_id):
    if request.method == 'POST' and request.body:
        try:
            conversation = Conversation.objects.get(id=int(conversation_id))
            if not conversation.users.filter(id=request.user.id):
                return HttpResponseForbidden()
            msg = conversation.send_message(request.user, request.body, request=request)
            response = json.dumps({'status': 'Ok', 'message': msg.to_dict})
        except Exception, e:
            response = json.dumps({'status': 'Error', 'exception_class': str(e.__class__),
                                   'exception_message': str(e.message) if e.message is not None else ''})
        return HttpResponse(response, content_type='application/json')

    return HttpResponseForbidden()


@login_required
def user_profile(request):
    template = loader.get_template('collaborative_crm/user_profile.html')
    context = {
        'web_title': 'LinkedProp | Perfil',
        'page_title': 'Perfil',
        'page_sub_title': u'Perfil de mi usuario',
        'page_name': 'news',
        'notification_types': NotificationType.objects.all(),
        'notification_tones': sorted(NotificationTone.objects.all(), key=lambda nt: nt.name if nt.id else '000')
    }
    return HttpResponse(template.render(context, request))


@login_required
@transaction.atomic
def change_password(request):
    if request.method == 'POST':
        if not request.user.check_password(request.POST.get('current-password')) or \
                        request.POST.get('new-password') != request.POST.get('new-password-repeat'):
            return HttpResponseForbidden()
        user = request.user
        user.set_password(request.POST.get('new-password'))
        user.save()
        login(request, authenticate(username=user.username, password=request.POST.get('new-password')))
        return redirect('collaborative_crm:user_profile')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def update_profile_data(request):
    if request.method == 'POST':
        first_name = request.POST.get('first-name', request.user.first_name)
        request.user.first_name = first_name if first_name else request.user.first_name
        last_name = request.POST.get('last-name', request.user.last_name)
        request.user.last_name = last_name if last_name else request.user.last_name
        request.user.save()
        request.user.userextension.telephone_number = request.POST.get('telephone-number')
        request.user.userextension.save()
        return redirect('collaborative_crm:user_profile')

    return HttpResponseForbidden()


@login_required
@transaction.atomic
def update_notifications_config(request):
    if request.method == 'POST':
        request.user.userextension.notifications_tone_id = int(request.POST.get('notifications-tone', 0))
        request.user.userextension.messages_tone_id = int(request.POST.get('messages-tone', 0))
        request.user.userextension.save()
        for notification_type_id in notification_types.values():
            try:
                unf = UserNotificationConfig.objects.get(user=request.user, notification_type_id=notification_type_id)
            except UserNotificationConfig.DoesNotExist:
                unf = UserNotificationConfig(user=request.user, notification_type_id=notification_type_id)

            unf.notify = request.POST.get('{0}-notify'.format(notification_type_id), False)
            unf.email = request.POST.get('{0}-email'.format(notification_type_id), False)
            unf.save()

        return redirect('collaborative_crm:user_profile')

    return HttpResponseForbidden()


def geography_hierarchy(request):
    return HttpResponse(
        json.dumps({
            'countries': [{'id': c.id, 'name': c.name} for c in Country.objects.all()],
            'states': [{'country_id': s.country.id, 'id': s.id, 'name': s.name} for s in State.objects.all()],
            'cities': [{'state_id': c.state.id, 'id': c.id, 'name': c.name} for c in City.objects.all()],
            'neighborhoods': [{'city_id': n.city.id, 'id': n.id, 'name': n.name} for n in Neighborhood.objects.all()]
        }), content_type='application/json')


@login_required
def geography_countries(request):
    return HttpResponse(json.dumps([c.to_dict for c in Country.objects.all()]), content_type='application/json')


@login_required
def geography_states(request, country_id):
    return HttpResponse(json.dumps([s.to_dict for s in State.objects.filter(country_id=int(country_id))]),
                        content_type='application/json')


@login_required
def geography_cities(request, state_id):
    return HttpResponse(json.dumps([c.to_dict for c in City.objects.filter(state_id=int(state_id))]),
                        content_type='application/json')


@login_required
def geography_neighborhoods(request, city_id):
    return HttpResponse(json.dumps([n.to_dict for n in Neighborhood.objects.filter(city_id=int(city_id))]),
                        content_type='application/json')


@login_required
def geography_search(request, entities, search_term):
    data = []
    entity_class_map = {
        'paises': Country,
        'estados': State,
        'ciudades': City,
        'barrios': Neighborhood
    }

    for entity in entities.split('-'):
        data.extend(list(entity_class_map[entity].objects.filter(name__unaccent__icontains=search_term.lower())))

    return HttpResponse(json.dumps([merge_two_dicts(elem.to_dict, {'type': elem.__class__.__name__.lower()})
                                    for elem in data]), content_type='application/json')


@login_required
def get_tone(request, extension, tone_id):
    tone = NotificationTone.objects.get(id=int(tone_id))
    return HttpResponse(open(tone.file_path(extension), 'rb'), content_type=NotificationTone.mime_types[extension])
