# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from ragendja.urlsauto import urlpatterns
from ragendja.auth.urls import urlpatterns as auth_patterns
#from myapp.forms import UserRegistrationForm
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

handler500 = 'ragendja.views.server_error'

site_patterns = patterns('',
    url(r'^account/logout', 'django.contrib.auth.views.logout', {'next_page': settings.LOGIN_URL}),
#    url(r'^account/logout', 'django.contrib.auth.views.logout', {'next_page': '/'}),
	(r'^i18n/', include('django.conf.urls.i18n')),

    ('^admin/(.*)', admin.site.root),
    (r'^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'about.html'}),
	(r'^about$', 'django.views.generic.simple.direct_to_template',
        {'template': 'about.html'}),        
	(r'^planning$', 'django.views.generic.simple.direct_to_template',
        {'template': 'gogogo/planning.html'}),                
	('^' ,include('gogogo.urls') ), 
	
    # Override the default registration form
 #   url(r'^account/register/$', 'registration.views.register',
 #       kwargs={'form_class': UserRegistrationForm},
 #       name='registration_register'),
)

if settings.ENABLE_GAEBAR:
    gaebar_patterns = patterns('',
        url(r'^gaebar/', include('gaebar.urls')),
        )
    urlpatterns = auth_patterns + site_patterns + gaebar_patterns  + urlpatterns    
else:
    urlpatterns = auth_patterns + site_patterns + urlpatterns
