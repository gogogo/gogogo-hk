# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import os

urlpatterns = patterns(
	'',
    (r'^agency$', 'gogogo.views.agency'),
    
    (r'^devtools/(?P<file>.*)$', 'gogogo.views.devtools'),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.abspath(os.path.dirname(__file__) + '/js') }  ),

)
