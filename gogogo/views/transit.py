"""
Show transit information for normal user. (Not a contributor)
"""
from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader , RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import ModelForm

from ragendja.auth.decorators import staff_only
from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from gogogo.models import *
from gogogo.geo.LatLng import LatLng
from widgets import Pathbar as _Pathbar
from gogogo.models.StopList import StopList
#import gogogo.views.widgets.Pathbar

class Pathbar(_Pathbar):
	"""
	A Pathbar for transit information
	"""
	def __init__(self,agency=None , stop = None):
		_Pathbar.__init__(self)
	
		self.append(_("Transit information") , 'gogogo.views.transit.index',None)
	
		if agency:
			try:
				self.append(agency[0]['name'] , 
					'gogogo.views.transit.agency' , [agency[0]['key_name']])
				self.append(agency[1]['long_name'] , 
					'gogogo.views.transit.route' , 
						[agency[0]['key_name'] , agency[1]['key_name']])
				self.append(agency[2]['headsign'] , 
					'gogogo.views.transit.trip' , 
						[agency[0]['key_name'] , agency[1]['key_name'],agency[2]['key_name']])					
			except IndexError:
				pass
				
		elif stop:
			self.append(stop['name'] , 'gogogo.views.transit.stop', [ stop['key_name']]  )		

def index(request):
	"""
	Show transit information
	"""

	pathbar = Pathbar()
	#pathbar.append(_("Transit information") , 'gogogo.views.transit.index',None)

	query = Agency.all()
	
	agency_list = []
	for row in query:
		entity = create_entity(row,request)
		entity['key_name'] = row.key().name()
		agency_list.append(entity)

	return render_to_response( 
		request,
		'gogogo/transit/index.html'
		,{ 
			'page_title': _("Transit information"),
			'pathbar' : pathbar,
		   "agency_list" : agency_list,
		   })		

def agency(request,agency_id):
	"""
	Browse the information of a transport agency
	"""

	try:
		key = db.Key.from_path(Agency.kind(),agency_id)
	
		record = db.get(key)
	except (db.BadArgumentError,db.BadValueError):
		raise Http404
	
	if record == None:
		raise Http404
		
	agency = create_entity(record,request)
	agency['key_name'] = record.key().name()
		
	gql = db.GqlQuery("SELECT * FROM gogogo_route where type = :1 and agency=:2",2,record)
	rail_list = []
	for row in gql:
		entity = create_entity(row,request)
		entity['key_name'] = row.key().name()
		rail_list.append(entity) 

	pathbar = Pathbar(agency=(agency,))
	#pathbar.append(_("Transit information") , 'gogogo.views.transit.index',None)
	#pathbar.append(agency['name'] , 'gogogo.views.transit.agency' , [agency['key_name']])
	
	t = loader.get_template('gogogo/transit/agency.html')
	c = RequestContext(
		request,
	{
        'page_title': agency['name'] ,
        'pathbar' : pathbar,
        'object_type' : 'agency',
        'agency' : agency,
        'rail_list' : rail_list
    })
    		
	return HttpResponse(t.render(c))

def route(request,agency_id,route_id):
	"""
	Browse the information of a route data. 
	
	It is the most expensive call in the system.
	"""
	
	agency_record = get_object_or_404(Agency,key_name=agency_id)
	record = get_object_or_404(Route,key_name=route_id)

	lang = MLStringProperty.get_current_lang(request)
	
	agency_entity = {
		'key_name': agency_record.key().name(),
		'name' : MLStringProperty.trans(agency_record.name,lang),
	}
	
	route_entity = {
		'key_name' : record.key().name(),
		'long_name' : MLStringProperty.trans(record.long_name,lang),
		'short_name' : record.short_name,
		'desc' : record.desc,
		
		# Reduce the no. of database access
		'agency' : agency_id
		#'agency' : record.agency.key().name()
	}
	
	gql = db.GqlQuery("SELECT * from gogogo_trip where route = :1",record)
	
	trip_list = []
	travel_list = []
	
	# Endpoint in all trip
	endpoint_list = []
	
	for trip_record in gql:
		stop_list = StopList(trip_record)
		
		travel_list.append( (MLStringProperty.trans(stop_list.first.name,lang),
			MLStringProperty.trans(stop_list.last.name,lang)))
		
		pt = LatLng(stop_list.first.latlng.lat,stop_list.first.latlng.lon )
		if pt not in endpoint_list:
			endpoint_list.append( pt )
		
		pt = LatLng(stop_list.last.latlng.lat,stop_list.last.latlng.lon )
		if pt not in endpoint_list:
			endpoint_list.append( pt )	
		
		trip_entity = {
			'headsign' : MLStringProperty.trans(trip_record.headsign,lang),
			'key_name' : trip_record.key().name(),
			'stop_list' : stop_list.createTREntity(request)
		}
		trip_list.append(trip_entity)
	
	#for trip_record in gql:
		#stop_list = []
		#try:
			#first_stop = db.get(trip_record.stop_list[0])
			#last_stop = db.get(trip_record.stop_list[len(trip_record.stop_list)-1])
			#travel_list.append( (MLStringProperty.trans(first_stop.name,lang),MLStringProperty.trans(last_stop.name,lang)))
			
			#pt = LatLng(first_stop.latlng.lat,first_stop.latlng.lon )
			#if pt not in endpoint_list:
				#endpoint_list.append( pt )
			
			#pt = LatLng(last_stop.latlng.lat,last_stop.latlng.lon )
			#if pt not in endpoint_list:
				#endpoint_list.append( pt )
		#except IndexError:
			#pass
			
		#for key in trip_record.stop_list:
			#stop = db.get(key)
			#stop_list.append( (key.name() , MLStringProperty.trans(stop.name,lang) ) )
		#trip_entity = {
			#'headsign' : MLStringProperty.trans(trip_record.headsign,lang),
			#'key_name' : trip_record.key().name(),
			#'stop_list' : stop_list
		#}
		#trip_list.append(trip_entity)

	pathbar = Pathbar(agency=(agency_entity,route_entity))

	return render_to_response( 
		request,
		'gogogo/transit/route.html'
		,{ 
			'page_title': route_entity['long_name'],
			'pathbar' : pathbar,
        	'object_type' : 'route',
		   "route" : route_entity,
		   "trip_list" : trip_list,
		   "travel_list" : travel_list,
		   "endpoint_list" : endpoint_list,
		   })		

def trip(request,agency_id,route_id,trip_id):
	"""
	Browse the information of a trip
	"""

	trip_record = get_object_or_404(Trip,key_name=trip_id)
	agency_record = get_object_or_404(Agency,key_name=agency_id)
	route_record = get_object_or_404(Route,key_name=route_id)
	
	lang = MLStringProperty.get_current_lang(request)
	
	trip_entity = {
		'key_name' : trip_record.key().name(),
		'short_name' : MLStringProperty.trans(trip_record.short_name,lang),
		'headsign' : MLStringProperty.trans(trip_record.headsign,lang),
	}
	
	agency_entity = {
		'key_name': agency_record.key().name(),
		'name' : MLStringProperty.trans(agency_record.name,lang),
	}
	
	route_entity = {
		'key_name' : route_record.key().name(),
		'long_name' : MLStringProperty.trans(route_record.long_name,lang),
	}
	
	shape_entity = None
	if trip_record.shape:
		shape_entity = {'points' : trip_record.shape.points,
			'color': trip_record.shape.color	}
	
	pathbar = Pathbar(agency=(agency_entity,route_entity,trip_entity))
	
	return render_to_response( 
		request,
		'gogogo/transit/trip.html'
		,{ 
			'page_title': trip_entity['headsign'],
			'pathbar': pathbar,
			'object_type' : 'trip',
			"agency" : agency_entity,
			"route" : route_entity,
		   "trip" : trip_entity,
		   "shape" : shape_entity
		   })		
	
	

def stop(request,stop_id):
	"""
	Browse stop information
	"""	
	try:
		key = db.Key.from_path(Stop.kind(),stop_id)
	
		record = db.get(key)
	except (db.BadArgumentError,db.BadValueError):
		raise Http404
		
	lang = MLStringProperty.get_current_lang(request)	
	stop_entity = {
		'key_name' : record.key().name(),
		'name' : MLStringProperty.trans(record.name,lang),
		'desc' : MLStringProperty.trans(record.desc,lang),
		'url' : record.url
	}

	pathbar = Pathbar(stop=stop_entity)
	#pathbar.append(_("Transit information") , 'gogogo.views.transit.index',None)
	#pathbar.append(stop_entity['name'] , 'gogogo.views.transit.stop', [ stop_entity['key_name']]  )

	return render_to_response( 
		request,
		'gogogo/transit/stop.html'
		,{ 
			'page_title': _("Transit information"),
			'pathbar' : pathbar,
		   "stop" : stop_entity,
		   })		
	