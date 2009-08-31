# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import os
import gogogo.api
import gogogo.views

urlpatterns = patterns(
	'',
	
	#Transit information (for general user)
	
	(r'^transit/agency/(?P<agency_id>[0-9a-zA-Z_-]+)/(?P<route_id>[0-9a-zA-Z_-]+)/(?P<trip_id>[0-9a-zA-Z_-]+)$', 'gogogo.views.transit.trip'),	
	(r'^transit/agency/(?P<agency_id>[0-9a-zA-Z_-]+)/(?P<route_id>[0-9a-zA-Z_-]+)$', 'gogogo.views.transit.route'),

	(r'^transit/agency/(?P<agency_id>[0-9a-zA-Z_-]+)$', 'gogogo.views.transit.agency'),
	(r'^transit/stop/(?P<stop_id>[0-9a-zA-Z_-]*)$', 'gogogo.views.transit.stop'),
	(r'^transit$', 'gogogo.views.transit.index'),

	#############################################################
	# Database frontend (for advanced viewing and editing)
	#############################################################
	(r'^db/shape/browse/(?P<id>[0-9a-zA-Z_]*)$' ,'gogogo.views.db.shape.browse'),
	
    (r'^db/agency/list$', 'gogogo.views.db.agency.list'),
	(r'^db/agency/browse/(?P<id>[0-9a-zA-Z_]*)$' ,'gogogo.views.db.agency.browse'),
	#(r'^db/agency/edit/(?P<id>[0-9a-zA-Z_]*)$' ,'gogogo.views.db.agency.edit'),
    (r'^db/route/search/$', 'gogogo.views.db.route.search'),
    #(r'^db/route/edit/(?P<id>[0-9a-zA-Z_]*)$', 'gogogo.views.db.route.edit'),
    (r'^db/changelog/list$', 'gogogo.views.db.changelog.list'),
    (r'^db/changelog/browse/(?P<id>[0-9a-zA-Z_-]+)$', 'gogogo.views.db.changelog.browse'),
    
    	#Report
    (r'^db/report/list$', 'gogogo.views.db.report.list'),
    (r'^db/(?P<kind>[a-z]+)/report/(?P<id>[0-9a-zA-Z_-]+)$', 'gogogo.views.db.report.submit'),
    
    # Generic model edit interface
    (r'^db/(?P<kind>[0-9a-zA-Z_]*)/edit/(?P<object_id>[0-9a-zA-Z_-]*)$', 'gogogo.views.db.edit'),
    
    # Generic model add interface
    (r'^db/(?P<kind>[0-9a-zA-Z_]+)/add$', 'gogogo.views.db.add'),

	################################################
	# Development tools
	################################################

	(r'^devtools/FindStopID$','gogogo.views.devtools.find_stop_id'),
	(r'^devtools/MassAddressQuery.html$', 'django.views.generic.simple.direct_to_template',
        {'template': 'gogogo/devtools/MassAddressQuery.html'}),
	(r'^devtools/StopMaps.html$', 'django.views.generic.simple.direct_to_template',
        {'template': 'gogogo/devtools/StopMaps.html'}),
    
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.abspath(os.path.dirname(__file__) + '/js') }  ),
    
    ################################################     
    # API     
    ################################################
         
	(r'^api/agency/list$' ,'gogogo.api.agency_list'),

	
	(r'^api/stop/search/(?P<lat0>[0-9]*\.[0-9]*),(?P<lng0>[0-9]*\.[0-9]*),(?P<lat1>[0-9]*\.[0-9]*),(?P<lng1>[0-9]*\.[0-9]*)$' 
		,'gogogo.api.stop.search'),
    (r'^api/stop/block$','gogogo.api.stop.block'),		
	(r'^api/stop/markerwin/(?P<id>[0-9a-zA-Z_]*)$' , 'gogogo.api.stop.markerwin'),
	(r'^api/stop/get$' ,'gogogo.api.stop.get'),		
	(r'^api/shape/get$' ,'gogogo.api.shape.get'),		

	(r'^api/trip/get$' ,'gogogo.api.trip_get'),
	
	(r'^api/cluster/search/(?P<lat0>[0-9]+\.*[0-9]*),(?P<lng0>[0-9]+\.*[0-9]*),(?P<lat1>[0-9]+\.*[0-9]*),(?P<lng1>[0-9]+\.*[0-9]*)$' 
		,'gogogo.api.cluster.search'),		
    (r'^api/cluster/block$','gogogo.api.cluster.block'),
    
    (r'^api/plan$','gogogo.api.plan.plan'),

)
