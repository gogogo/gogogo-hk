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

def _get(id,request):
    """
    Get a trip entity
    """
    entity = getCachedEntityOr404(Trip,id_or_name = id)
    entity = trEntity(entity,request)
    del entity['instance']
        
    if entity["route"]:
        if isinstance(entity["route"],db.Key):
            route = getCachedEntityOr404(Route,key = entity["route"])
        else:
            route = getCachedEntityOr404(Route,id_or_name = entity["route"])
        route = trEntity(route,request)
        entity['color'] = route["color"]
        entity['name'] = route["long_name"]
        
    return entity


def get(request):
    if "id" not in request.GET:
        return ApiResponse(error="ID missing")
        
    id = request.GET['id']
    entity = _get(id,request)
               
    return ApiResponse(data=entity)

def mget(request):
    """
    Get multiple entities in an ajax call
    """
    if "ids" not in request.GET:
        return ApiResponse(error="ids missing")
        
    ids = request.GET['ids']

    items = ids.split(",")

    result = []

    for id in items:    
        try:
            entity = _get(id,request)
            result.append(entity)

        except Http404:
            pass

    return ApiResponse(data=result)
