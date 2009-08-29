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

_default_cache_time = 3600

from google.appengine.api import memcache
			
def get(request):
    if "id" not in request.GET:
        return ApiResponse(error="ID missing")
        
    id = request.GET['id']
        
    try:
        entity = getCachedEntityOr404(Shape,id_or_name = id)

        del entity['owner']
        del entity['instance']
        del entity['owner_kind']
        return ApiResponse(data=entity)
    except Http404:
        return ApiResponse(error="Shape not found")
	

