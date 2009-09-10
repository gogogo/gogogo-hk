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
from gogogo.algo.TransitGraph import StopGraph
from gogogo.algo.path import mst
import logging

_default_cache_time = 3600

from google.appengine.api import memcache
			
def get(request):
    if "id" not in request.GET:
        return ApiResponse(error="ID missing")
        
    id = request.GET['id']
        
    try:
        entity = getCachedEntityOr404(Agency,id_or_name = id)
        entity = trEntity(entity,request)
        del entity['instance']

        return ApiResponse(data=entity)
    except Http404:
        return ApiResponse(error="Agency not found")
	
def list(request):
    """
    Handle api/agency/list
    """
    query = Agency.all()
    text = StringIO()

    result = []
    for agency in query:
        result.append(create_entity(agency,request))

    return ApiResponse(data=result)

def path(request):
    """
    Query the shape of a path from a stop to another stop using specific agency
    """
    if "id" not in request.GET or "from" not in request.GET or "to" not in request.GET:
        return ApiResponse(error="Argument missing")
        
    id = request.GET["id"]
    from_stop = request.GET["from"]
    to_stop = request.GET["to"]
    
    #TODO , cache the result
    
    graph = StopGraph.create(id)
    src = graph.get_node_by_stop_id(from_stop)
    dest = graph.get_node_by_stop_id(to_stop)
    if src == None:
       return ApiResponse(error="%s not found" % from_stop )
    
    if dest == None:
       return ApiResponse(error="%s not found" % to_stop )
    
    (backtrack,weight) = mst(graph,src)
    
    if weight[dest.id] > graph.get_node_count():
        return ApiResponse(error="No path existed" % to_stop )

    stop_id = []
    current = dest
    while current.name != src.name:
        stop_id.insert(0,current.name)
        current = backtrack[current.id].src
    stop_id.insert(0,src.name)
    
    return ApiResponse(data=stop_id)
