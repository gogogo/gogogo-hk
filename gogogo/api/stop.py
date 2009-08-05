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
from gogogo.models.cache import getCachedObjectOr404
from gogogo.models.cache import getCachedEntityOr404
import logging

_default_cache_time = 3600

def search(request,lat0,lng0,lat1,lng1):
	"""
		Search stop (api/stop/search)
	"""
	lat0 = float(lat0)
	lng0 = float(lng0)
	lat1 = float(lat1)
	lng1 = float(lng1)
	
	if lat0 < lat1:
		minlat = lat0
		maxlat = lat1
	else:
		minlat = lat1
		maxlat = lat0
	
	if lng0 < lng1:
		minlng = lng0
		maxlng = lng1
	else:
		minlng = lng1
		maxlng = lng0
		
	#TODO: Check the distance. Prevent to dump the database that will spend too much bandwidth
	hash0 = str(Geohash( (minlng,minlat) ))
	hash1 = str(Geohash( (maxlng,maxlat) ))

	result = []
	
	lang = MLStringProperty.get_current_lang(request)	
	
	query = Stop.all().filter("geohash >=" , hash0).filter("geohash <=" , hash1)
	
	for stop in query:
		#TODO: Check again for real lat/lng value
		entity = {
			"id" : stop.key().name(),
			"name" : MLStringProperty.trans(stop.name,lang),
			"url" : stop.url,
			"latlng" : stop.latlng,
			"agency" : stop.agency,
		}
		result.append(entity)
	
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
			
		cache['trip_list']  = trip_list
				
		#memcache.add(cache_key, cache, _default_cache_time):
		
	t = loader.get_template('gogogo/api/stop-markerwin.html')
	c = Context(
	{
        'stop': trEntity(stop,request),
        #'stop' : stop,
        'trip_list' : cache['trip_list']
	})
    		
	return HttpResponse(t.render(c))
