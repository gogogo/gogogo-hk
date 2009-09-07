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
from gogogo.models.loaders import AgencyLoader,RouteLoader,TripLoader, ListLoader
from gogogo.models.property import TransitTypeProperty
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
					'gogogo.views.transit.agency' , [agency[0]['id']])
				self.append(agency[1]['long_name'] , 
					'gogogo.views.transit.route' , 
						[agency[0]['id'] , agency[1]['id']])
				self.append(agency[2]['headsign'] , 
					'gogogo.views.transit.trip' , 
						[agency[0]['id'] , agency[1]['id'],agency[2]['id']])					
			except IndexError:
				pass
				
		elif stop:
			self.append(stop['name'] , 'gogogo.views.transit.stop', [ stop['id']]  )		

def index(request):
    """
    Show transit information
    """

    pathbar = Pathbar()
    #pathbar.append(_("Transit information") , 'gogogo.views.transit.index',None)

    loader = ListLoader(Agency)
    loader.load()

    data = loader.get_data()
    agency_list = []
    for agency in data:
        entity = createEntity(agency)
        entity = trEntity(entity,request)
        entity["type_name"] = TransitTypeProperty.get_type_name(entity["type"])
        
        agency_list.append(entity)

    return render_to_response( 
        request,
        'gogogo/transit/index.html'
        ,{ 
            'page_title': _("Transit information"),
            'pathbar' : pathbar,
            'model_kind' : "agency",
           "agency_list" : agency_list,
           "agency_type_list" : TransitTypeProperty.get_basic_type_name_list()
           })		

def agency(request,agency_id):
    """
    Browse the information of a transport agency
    """
    
    agency_loader = AgencyLoader(agency_id)
    agency_loader.load(request)

    agency = trEntity(agency_loader.get_agency_entity(),request)
    agency["type"] = TransitTypeProperty.get_type_name(agency["type"])
    
    pathbar = Pathbar(agency=(agency,))
   
    route_list = agency_loader.get_route_list()
    route_list = [trEntity(route,request) for route in route_list]
    
    trip_id_list = agency_loader.get_trip_id_list()
    
    showMap = agency["show_map_in_transit_page"]

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
        'route_list' : route_list
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

    agency_entity = trEntity(route_loader.get_agency(),request)
    route_entity = trEntity(route_loader.get_entity(),request)
    route_entity['type'] = TransitTypeProperty.get_type_name(route_entity['type'])

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
    
    trip_loader = TripLoader(trip_id)
    trip_loader.load()

    trip_entity = trip_loader.get_trip()
    agency_entity = trip_loader.get_agency()
    route_entity = trip_loader.get_route()

    trip_entity = trEntity(trip_entity,request)
    agency_entity = trEntity(agency_entity,request)
    route_entity = trEntity(route_entity,request)
    stop_list = [trEntity(stop,request) for stop in trip_loader.get_stop_list() ]
    
    faretrip_list = []
    for faretrip in trip_loader.get_faretrip_list():
        entity = trEntity(faretrip,request)
        entity["fare_range"] = None
        if entity["max_fare"] > 0 :
            if entity["max_fare"] != entity["min_fare"]:
                entity["fare_range"] = "$%0.1f - $%0.1f" % (entity["min_fare"],entity["max_fare"])
            else:
                entity["fare_range"] = "$%0.1f" % (entity["min_fare"])
        
        faretrip_list.append(entity)
        
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
           "stop_list" : stop_list,
           "faretrip_list" : faretrip_list,
           "faretrip_kind" : "faretrip"
           })		
	

def stop(request,stop_id):
	"""
	Browse stop information
	"""	
	entity = getCachedEntityOr404(Stop,id_or_name = stop_id)

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
