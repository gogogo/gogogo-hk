# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import os
import gogogo.api

urlpatterns = patterns(
	'',
    (r'^agency/list$', 'gogogo.views.agency_list'),
    
    (r'^devtools/(?P<file>.*)$', 'gogogo.views.devtools'),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.abspath(os.path.dirname(__file__) + '/js') }  ),
         
    # API     
         
	(r'^api/agency/list$' ,'gogogo.api.agency_list'),
	
	(r'^api/stop/search/(?P<lat0>[0-9]*\.[0-9]*),(?P<lng0>[0-9]*\.[0-9]*),(?P<lat1>[0-9]*\.[0-9]*),(?P<lng1>[0-9]*\.[0-9]*)$' 
		,'gogogo.api.stop_search'),

)
