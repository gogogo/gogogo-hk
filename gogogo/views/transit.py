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
from gogogo.models.cache import getCachedObjectOr404 , getCachedEntityOr404
from gogogo.models.loaders import RouteLoader,TripLoader
from google.appengine.api import memcache


_default_cache_time = 3600

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
		entity['key_name'] = row.key().id_or_name()
		agency_list.append(entity)

	return render_to_response( 
		request,
		'gogogo/transit/index.html'
		,{ 
			'page_title': _("Transit information"),
			'pathbar' : pathbar,
			'model_kind' : "agency",
		   "agency_list" : agency_list,
		   })		

def agency(request,agency_id):
	"""
	Browse the information of a transport agency
	"""

	cache_key = "gogogo__transit_agency_%s" % agency_id #Prefix of memecache key

	cache = memcache.get(cache_key)
	
	if cache == None:
		entity = getCachedEntityOr404(Agency,id_or_name = agency_id)

		cache = {}
		cache['agency'] = entity
		
		railway_list = []
		trip_id_list = []
		
		# Query for railway information
		gql = db.GqlQuery("SELECT * FROM gogogo_route where type = :1 and agency=:2",2,entity['instance'])
		
		for row in gql:		
			e = createEntity(row)
			railway_list.append(e)
			
			queryTrip = db.GqlQuery("SELECT * from gogogo_trip where route = :1",row)
			for trip in queryTrip:
				trip_id_list.append(trip.key().id_or_name())
			
		if len(railway_list) > 0:
			cache['showMap'] = True
		else:
			cache['showMap'] = False
			
		cache['railway_list'] = railway_list
		cache['trip_id_list'] = trip_id_list
		memcache.add(cache_key, cache, _default_cache_time)

	agency = trEntity(cache['agency'],request)
	pathbar = Pathbar(agency=(agency,))
	
	showMap = cache['showMap']
	railway_list = [ trEntity(e,request) for e in cache['railway_list'] ]
	trip_id_list = cache['trip_id_list']
	
	t = loader.get_template('gogogo/transit/agency.html')
	c = RequestContext(
		request,
	{
        'page_title': agency['name'] ,
        'pathbar' : pathbar,
        'agency_kind' : 'agency',
        'route_kind' : 'route',
        'agency' : agency,
        'showMap' : showMap,
        'trip_id_list' : trip_id_list,
        'railway_list' : railway_list
    })
    		
	return HttpResponse(t.render(c))

def route(request,agency_id,route_id):
	"""
	Browse the information of a route data. 
	
	It is the most expensive call in the system.
	"""
	
	route_loader = RouteLoader(route_id)
	route_loader.load()
	
	lang = MLStringProperty.get_current_lang(request)
	
	#agency_entity = getCachedEntityOr404(Agency,id_or_name=agency_id)	
	#route_entity = getCachedEntityOr404(Route,id_or_name=route_id)
	
	#TODO - memcache	
	#gql = db.GqlQuery("SELECT * from gogogo_trip where route = :1",route_entity['instance'])
	
	#trip_list = []
	#travel_list = []
	#trip_id_list = []
	
	## Endpoint in all trip
	#endpoint_list = []
	
	#for trip_record in gql:
		#stop_list = StopList(trip_record)
		
		#travel_list.append( (MLStringProperty.trans(stop_list.first.name,lang),
			#MLStringProperty.trans(stop_list.last.name,lang)))
		
		#pt = LatLng(stop_list.first.latlng.lat,stop_list.first.latlng.lon )
		#if pt not in endpoint_list:
			#endpoint_list.append( pt )
		
		#pt = LatLng(stop_list.last.latlng.lat,stop_list.last.latlng.lon )
		#if pt not in endpoint_list:
			#endpoint_list.append( pt )	
		
		#trip_entity = {
			#'headsign' : MLStringProperty.trans(trip_record.headsign,lang),
			#'id' : trip_record.key().id_or_name(),
			#'stop_list' : stop_list.createTREntity(request)
		#}
		
		#trip_id_list.append(trip_record.key().id_or_name())
		#trip_list.append(trip_entity)
	
	agency_entity = trEntity(route_loader.get_agency(),request)
	route_entity = trEntity(route_loader.get_entity(),request)
	route_entity['type'] = Route.get_type_name(route_entity['type'])
	
	trip_list = []
	
	endpoint_id_list = {}
	endpoint_list = []
	
	for trip_loader in route_loader.get_trip_list():
		entity = trEntity(trip_loader.get_entity(),request)
		entity['first'] = trEntity(trip_loader.first,request)		
		entity['last'] = trEntity(trip_loader.last,request)
		entity['stop_list'] = [ trEntity(stop,request) for stop in trip_loader.stop_entity_list ]
		trip_list.append(entity)
		
		for type in ("first","last"):
			stop = entity[type]
			if stop == None:
				continue
			id = stop['id']
			if  id not in endpoint_id_list:
				endpoint_id_list[id] = True;
				endpoint_list.append(stop['latlng'].lat)
				endpoint_list.append(stop['latlng'].lon)

	trip_id_list = [ trip['id'] for trip in trip_list]
	pathbar = Pathbar(agency=(agency_entity,route_entity,))
	
	return render_to_response( 
		request,
		'gogogo/transit/route.html'
		,{ 
			'page_title': agency_entity['name'] + " - " + route_entity['long_name'],
			'pathbar' : pathbar,
        	'route_kind' : 'route',
        	'trip_kind' : 'trip',
        	"agency" : agency_entity,
		   "route" : route_entity,
		   "trip_list" : trip_list,
		   #"travel_list" : travel_list,
		   "endpoint_list" : endpoint_list,
		   
		   "trip_id_list" : trip_id_list
		   })		

def trip(request,agency_id,route_id,trip_id):
	"""
	Browse the information of a trip
	"""

	trip_entity = getCachedEntityOr404(Trip,id_or_name=trip_id)
	trip_record = trip_entity['instance']
	agency_entity = getCachedEntityOr404(Agency,id_or_name=agency_id)
	route_entity = getCachedEntityOr404(Route,id_or_name=route_id)
	
	# lang = MLStringProperty.get_current_lang(request)
	
	#trip_entity = {
		#'key_name' : trip_record.key().name(),
		#'short_name' : MLStringProperty.trans(trip_record.short_name,lang),
		#'headsign' : MLStringProperty.trans(trip_record.headsign,lang),
	#}
	
	#agency_entity = {
		#'key_name': agency_record.key().name(),
		#'name' : MLStringProperty.trans(agency_record.name,lang),
	#}
	
	#route_entity = {
		#'key_name' : route_record.key().name(),
		#'long_name' : MLStringProperty.trans(route_record.long_name,lang),
	#}
	
	trip_entity = trEntity(trip_entity,request)
	agency_entity = trEntity(agency_entity,request)
	route_entity = trEntity(route_entity,request)
	
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
	entity = getCachedEntityOr404(Stop,key_name = stop_id)

	entity = trEntity(entity,request)		
	pathbar = Pathbar(stop=entity)
	
	parent = None
	if 'parent_station' in entity and entity['parent_station'] != None:
		parent = getCachedEntityOr404(Stop,id_or_name = entity['parent_station'].id_or_name())
		parent = trEntity(parent,request)

	t = loader.get_template('gogogo/transit/stop.html')
	c = RequestContext(
		request,
	{
		'page_title': entity['name'] ,
		'pathbar' : pathbar,
		'parent' : parent,
		'stop_kind' : "stop",
	   	"stop" : entity,
    })
    		
	return HttpResponse(t.render(c))
