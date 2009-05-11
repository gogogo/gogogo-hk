# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
from appenginepatcher import on_production_server

urlpatterns = patterns('')
if not on_production_server:
    urlpatterns = patterns('',
        (r'^%s(?P<path>.+)$' % settings.MEDIA_URL.lstrip('/'),
            'mediautils.views.get_file'),
    )
