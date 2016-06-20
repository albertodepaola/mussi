#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from collaborative_crm.models import *
import json


def login_page(request):
    if request.user and request.user.is_active:
        return redirect('collaborative_crm:home')
    template = loader.get_template('collaborative_crm/login.html')
    context = {'web_title': 'LinkedProp | Log In'}
    request.session['redirect'] = request.GET.get('next', '')
    return HttpResponse(template.render(context, request))


def login_user(request):
    redirect = request.session.get('redirect')
    if request.method == 'POST':
        logout(request)
        parameters = json.loads(request.body)
        try:
            user_object = User.objects.get(username=parameters.get('username'))
            user = authenticate(username=parameters.get('username'), password=parameters.get('password'))
            if user is not None:
                if user.is_active:
                    user_object.successful_login()
                    login(request, user)
                    response = {'status': 'Ok', 'redirect': redirect if redirect else reverse('collaborative_crm:home')}
                else:
                    response = {'status': 'Error', 'error_message': u'Usuario bloqueado, contáctenos para debloquearlo'}
            else:
                user_object.failed_login()
                if user_object.is_active:
                    msg = 'Credenciales incorrectas, {0} intentos antes del bloqueo'.format(
                        user_object.login_attempts_remaining)
                else:
                    msg = u'Usuario bloqueado, contáctenos para debloquearlo'
                response = {'status': 'Error', 'error_message': msg}
        except User.DoesNotExist:
            response = {'status': 'Error', 'error_message': 'Usuario inexistente'}

        request.session['redirect'] = redirect
        return HttpResponse(json.dumps(response), content_type='application/json')

    return HttpResponseForbidden()


def reset_password_email(request):
    if request.method == 'POST' and not request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.body)
            if not user.is_active:
                return HttpResponseForbidden()
            new_password = user.generate_random_password()
            user.set_password(new_password)
            user.save()
            template = loader.get_template('collaborative_crm/email_password_reset.html')
            template_plain = loader.get_template('collaborative_crm/email_password_reset_plain.txt')
            context = {
                'request_user': user,
                'new_password': new_password,
                'link_to_login': request.build_absolute_uri(reverse('login_page')),
                'linked_prop_email': linked_prop_email,
                'linked_prop_telephone': linked_prop_telephone
            }
            create_html_plain_email(u'[LinkedProp] Solicitud de restauración de password',
                                    template_plain.render(context, request), template.render(context, request),
                                    [user.username]).send()
            return redirect('login_page')
        except User.DoesNotExist:
            return HttpResponseForbidden()
    return HttpResponseForbidden()


@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login_page')


@login_required
def existing_usernames(request):
    return HttpResponse(json.dumps([u.username for u in User.objects.all()]), content_type='application/json')


def favicon(request):
    return HttpResponse(open('{0}{1}'.format(settings.MEDIA_URL, 'favicon.ico'), 'rb'), content_type='image/x-icon')


def error_400(request):
    if request.user and not request.user.is_authenticated():
        return redirect('collabortaive_crm:login')
    template = loader.get_template('collaborative_crm/error404.html')
    context = {
        'web_title': u'LinkedProp | Pagina no existe',
        'linked_prop_email': linked_prop_email,
        'linked_prop_telephone': linked_prop_telephone
    }
    return HttpResponseNotFound(template.render(context, request))


def error_403(request):
    if request.user and not request.user.is_authenticated():
        return redirect('collabortaive_crm:login')
    template = loader.get_template('collaborative_crm/error404.html')
    context = {
        'web_title': u'LinkedProp | Pagina no existe',
        'linked_prop_email': linked_prop_email,
        'linked_prop_telephone': linked_prop_telephone

    }
    return HttpResponseNotFound(template.render(context, request))


def error_404(request):
    if request.user and not request.user.is_authenticated():
        return redirect('collabortaive_crm:login')
    template = loader.get_template('collaborative_crm/error404.html')
    context = {
        'web_title': u'LinkedProp | Pagina no existe',
        'linked_prop_email': linked_prop_email,
        'linked_prop_telephone': linked_prop_telephone

    }
    return HttpResponseNotFound(template.render(context, request))


def error_500(request):
    if request.user and not request.user.is_authenticated():
        return redirect('collabortaive_crm:login')
    template = loader.get_template('collaborative_crm/error500.html')
    context = {
        'web_title': u'LinkedProp | Pagina no existe',
        'linked_prop_email': linked_prop_email,
        'linked_prop_telephone': linked_prop_telephone
    }
    return HttpResponseServerError(template.render(context, request))
