"""mussi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from mussi import views

urlpatterns = [
    url(r'^$', views.login_page, name='login_page'),
    url(r'^login$', views.login_page, name='login_page'),
    url(r'^reset_password_email$', views.reset_password_email, name='reset_password_email'),
    url(r'^login_usuario$', views.login_user, name='login_user'),
    url(r'^logout_usuario$', views.logout_user, name='logout_user'),
    url(r'^usuarios_existentes$', views.existing_usernames, name='existing_usernames'),

    url(r'^favicon\.ico$', views.favicon, name='favicon'),

    url(r'^crm/', include('collaborative_crm.urls')),

    url(r'^admin/', admin.site.urls),
]

handler400 = views.error_400
handler403 = views.error_403
handler404 = views.error_404
handler500 = views.error_500
