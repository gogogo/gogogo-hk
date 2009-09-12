from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader
from django.conf import settings

from django.utils import simplejson
from StringIO import StringIO
from google.appengine.api import memcache
from google.appengine.ext import db

from gogogo.models import *
from gogogo.geo.geohash import Geohash

from . import ApiResponse
from gogogo.models.cache import getCachedObjectOr404 , getCachedEntityOr404
from gogogo.models.utils import createEntity, trEntity , latlngFromGeoPt
from gogogo.models.loaders import StopLoader
from gogogo.geo import LatLng , LatLngBounds

import logging

_default_cache_time = 3600

def search(request,lat0,lng0,lat1,lng1):
    """
        Search stop (api/stop/search)
        Deprecated
        
    """
    lat0 = float(lat0)
    lng0 = float(lng0)
    lat1 = float(lat1)
    lng1 = float(lng1)

    sw = LatLng(lat0,lng0)
    ne = LatLng(lat1,lng1)
    bounds = LatLngBounds(sw,ne)
        
    #TODO: Check the distance. Prevent to dump the database that will spend too much bandwidth
    hash0 = str(Geohash( (sw.lng,sw.lat) ))
    hash1 = str(Geohash( (ne.lng,ne.lat) ))

    lang = MLStringProperty.get_current_lang(request)

    cache_key = "gogogo_stop_search_%d_%s_%s" % (lang,hash0,hash1)

    cache = memcache.get(cache_key)

    if cache == None:
        result = []

        query = Stop.all().filter("geohash >=" , hash0).filter("geohash <=" , hash1)
        
        for stop in query:
            pt = latlngFromGeoPt(stop.latlng)
            if bounds.containsLatLng(pt):
                entity = createEntity(stop)
                entity = trEntity(entity,request)
                del entity['instance']
                del entity['geohash']
                result.append(entity)
        
        cache = {}
        cache['result'] = result	
        memcache.add(cache_key, cache, _default_cache_time)

    result = cache['result']

    return ApiResponse(data=result)

def block(request):
    if "prefix" not in request.GET:
        return ApiResponse(error="Prefix missing")
        
    prefix = request.GET['prefix']

    if len(prefix) <= 4:
        return ApiResponse(error="The query range is too large")

    lang = MLStringProperty.get_current_lang(request)

    cache_key = "gogogo_stop_block_%d_%s" % (lang,prefix)
    cache = memcache.get(cache_key)

    if cache == None:           
        query = Stop.all(keys_only=True).filter("geohash >=" , prefix ).filter("geohash <=" , prefix + 'zzzzzz')
        
        result = []
        for key in query:
            entity = getCachedEntityOr404(Stop,key = key)
            entity = trEntity(entity,request)
            del entity['instance']
            del entity['geohash']           
            result.append(entity)
        
        cache = {}
        cache['result'] = result
        
        memcache.add(cache_key, cache, _default_cache_time)
        
    result = cache['result']
    
    return ApiResponse(data=result)
    

def markerwin(request,id):
	"""
	Generate marker window
	"""
	
	cache_key = "gogogo__stop_markerwin_%s" % id #Prefix of memecache key
	
	cache = memcache.get(cache_key)

	if cache == None:

		stop = getCachedEntityOr404(Stop,key_name=id)

		cache = {}
		cache['stop'] = stop
		
		trip_list = []	
	
		
		if  stop['parent_station'] == None:
			station_key = stop['instance'].key()
		else:
			#station_key = db.Key.from_path(Stop.kind(),stop['parent_station'])
			#logging.info(station_key)
			#parent_station = getCachedEntityOr404(Stop,key = station_key)
			station_key = stop['instance'].parent_station.key()
			cache['parent_station'] = createEntity(stop['instance'].parent_station)
		
		q = Trip.all().filter("stop_list = " , station_key)
		for row in q:
			trip = createEntity(row)
			
			trip['route_id'] = trip['instance'].route.key().id_or_name()
			
			trip['agency_id'] = trip['instance'].route.agency.key().id_or_name()
			trip_list.append(trip)
						
		cache['trip_list'] = trip_list
				
		memcache.add(cache_key, cache, _default_cache_time)
		
	stop = trEntity(cache['stop'],request)
	trip_list = [trEntity(trip,request) for trip in cache['trip_list']   ]
	
	parent_station = None
	if 'parent_station' in cache:
		parent_station = trEntity(cache['parent_station'],request)
		
	t = loader.get_template('gogogo/api/stop-markerwin.html')
	c = Context(
	{
        'stop': stop,
        'parent_station' : parent_station,
        'trip_list' : trip_list
	})
    		
	return HttpResponse(t.render(c))

def get(request):
    if "id" not in request.GET:
        return ApiResponse(error="ID missing")
        
    id = request.GET['id']
        
    try:
        entity = getCachedEntityOr404(Stop,id_or_name = id)
        entity = trEntity(entity,request)
        del entity['instance']
        del entity['geohash']
        return ApiResponse(data=entity)
    except Http404:
        return ApiResponse(error="Stop not found")
	
def list_trip(request):
    if "id" not in request.GET:
        return ApiResponse(error="ID missing")    
        
    id = request.GET['id']
    
    loader = StopLoader(id)
    loader.load()
    
    trip_id_list = loader.get_trip_id_list()
    
    return ApiResponse(data=trip_id_list)

def mget(request):
    """
    Get multiple stop in an ajax call
    """
    if "input" not in request.GET:
        return ApiResponse(error="input")
        
    input = request.GET['input']

    items = input.split(",")

    result = []

    for id in items:    
        try:
            entity = getCachedEntityOr404(Stop,id_or_name = id)
            entity = trEntity(entity,request)
            del entity['geohash']
            del entity['instance']
            result.append(entity)

        except Http404:
            pass

    return ApiResponse(data=result)
