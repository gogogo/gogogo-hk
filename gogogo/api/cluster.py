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
import logging
import math

_default_cache_time = 3600

from google.appengine.api import memcache

def search(request,lat0,lng0,lat1,lng1):
	"""
	Cluster searching

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
	
	cache_key = "gogogo_cluster_search_%s_%s" % (hash0,hash1)
	cache = memcache.get(cache_key)
	
	if cache == None:
		query = Cluster.all(keys_only=True).filter("geohash >=" , hash0).filter("geohash <=" , hash1)
		
		result = []
		for key in query:
			entity = getCachedEntityOr404(Cluster,id_or_name = key.id_or_name())
			del entity['instance']
			del entity['geohash']
			entity['radius'] = "%0.3f" % entity['radius']
			result.append(entity)
		
		cache = {}
		cache['result'] = result
		
		memcache.add(cache_key, cache, _default_cache_time)
		
	result = cache['result']
	
	return ApiResponse(data=result)

