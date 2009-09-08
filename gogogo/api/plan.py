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
from gogogo.algo import TransitGraph
import logging
import math

_default_cache_time = 3600

from google.appengine.api import memcache

def plan(request):
    if "from" not in request.GET or "to" not in request.GET:
        return ApiResponse(error="Argument missing")

    from_cluster = request.GET["from"]
    to_cluster = request.GET["to"]
        
    graph = TransitGraph.create()
    
    a = graph.get_node(from_cluster)
    b = graph.get_node(to_cluster)
    arcs = graph.search_arcs(a,b)
    
    result = {
        "from" : a.id,
        "to" : b.id,
        "count" : len(arcs),
        "fares" : [ arc.weight for arc in arcs]
    }
    return ApiResponse(data=result)
