# -*- coding: utf-8 -*-
from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from TitledStringListProperty import TitledStringListProperty
from django.utils.translation import ugettext_lazy as _
from ragendja.dbutils import get_object
from gogogo.geo.geohash import Geohash
from django.http import Http404

from utils import createEntity , entityToText , id_or_name
from cache import getCachedEntityOr404 , getCachedObjectOr404
from MLStringProperty import MLStringProperty

from google.appengine.api import memcache
from . import Route , Trip , Stop , Agency
from StopList import StopList
import logging
import sys

_default_cache_time = 3600

class Loader:
    """
    Abstract based class for all Loader class.

    Sub-class must provide following attributes:

    cache_key_prefix = The prefix of cache key 
    """

    def get_entity(self):
        return self.entity

    def get_cache_key(self,lang=None):
        if lang == None and hasattr(self,"lang"):
            lang = self.lang
        if lang != None:
            return "%s_%s_%d" % (self.cache_key_prefix , str(self.id) , lang)
        return self.cache_key_prefix + "_" + str(self.id)
        
    def remove_cache(self):
        cache_key = self.get_cache_key()
        memcache.delete(cache_key)

class FareStopLoader(Loader):
    """
    FareStop loading and cache management
    """
    
    def __init__(self,id):
        self.id = id_or_name(id)
        self.cache_key_prefix = "gogogo_farestop_loader_"
        
    def load(self):
        """
        Load from memcache or bigtable.
        
        Remark : If you only want to load a single entry of Agency , please use
        getCachedEntityOr404 instead.
        """
        cache_key = self.get_cache_key()
        
        cache = memcache.get(cache_key)

        if cache == None:
            cache = {}
            
            entity = getCachedEntityOr404(Agency,id_or_name = self.id)
            cache['farestop'] = entity
            farestop = entity['instance']
            
            pair_list = []
            for pair in farestop.pair_set:
                pair_list.append(createEntity(pair))
                
            cache['pair_list'] = pair_list
            
            memcache.add(cache_key, cache, _default_cache_time)
    
        self.farestop = cache['farestop']
        self.pair_list = cache['pair_list']
        
    def get_farestop():
        return self.farestop
        
    def load_for_agency(agency):
        """
       Load a list of FareStopLoader for an agency
        """
        if isinstance(agency,db.Key):
            key = agency
        else:
            key = agency.key()
        
        query = db.GqlQuery("SELECT __key__ from gogogo_farestop WHERE owner = :1",key)
        
        ret = []
        for key in query:
            loader = FareStopLoader(key.id_or_name())
            loader.load()
            ret.append(loader)
            
        return ret
    
    load_for_agency = staticmethod(load_for_agency)
        

class AgencyLoader(Loader):
    """
    Agency data loading and cache management
    """
    
    def __init__(self,id):
        self.id = id_or_name(id)
        self.cache_key_prefix = "gogogo_agency_loader_"
        
        self.agency = None # A tr entity 
        self.routes = None # An array of route tr entity
        self.trips = None # A dict of trip key with using route as key
        
    def load(self):
        """
        Load from memcache or bigtable.
        
        Remark : If you only want to load a single entry of Agency , please use
        getCachedEntityOr404 instead.
        """
        cache_key = self.get_cache_key()
        
        cache = memcache.get(cache_key)

        if cache == None:
            cache = {}
            entity = getCachedEntityOr404(Agency,id_or_name = self.id)
            agency = entity["instance"]
            
            cache["agency"] = entity
            
            property = getattr(Trip,"route")
            route_entity_list = []
            trip_key_list = {}
            
            gql = db.GqlQuery("SELECT * FROM gogogo_route where agency=:1",agency)
            
            for row in gql:		
                e = createEntity(row)
                route_entity_list.append(e)
                gql2 = db.GqlQuery("SELECT __key__ FROM gogogo_trip where route = :1",row)
                
                route_key = row.key().id_or_name()
                for trip in gql2:
                    if not route_key in trip_key_list:
                        trip_key_list[route_key] = []
                    trip_key_list[route_key].append(trip)

            cache["routes"] = route_entity_list
                        
            cache["trips"] = trip_key_list
            
            memcache.add(cache_key, cache, _default_cache_time)
            
        self.agency = cache["agency"]
        self.routes = cache["routes"]
        self.trips = cache["trips"]
        
    def get_agency_entity(self):
        return self.agency
        
    def get_route_list(self):
        return self.routes
        
    def get_trip_id_list(self):
        """
        Get all the trip id.
        """
        ret = []
        for key in self.trips:
            trips = self.trips[key]
            for trip in trips:
                ret.append(trip.id_or_name())
        
        return ret

class TripLoader(Loader):
    """
    Trip and related object loader and cache management

    """
    def __init__(self,id):
        self.id = id_or_name(id)
        self.cache_key_prefix = "gogogo_trip_loader_"

    def load(self):
        """
        Load trip and all related objects from memecache or bigtable.
        
        If you only want to load a single entry of Trip , please use
        getCachedEntityOr404 instead.
        """
        
        cache_key = self.get_cache_key()
        
        cache = memcache.get(cache_key)
        
        if cache == None:
            cache = {}
            
            trip_entity = getCachedEntityOr404(Trip,id_or_name = self.id)
            trip = trip_entity['instance']
            cache['trip'] = trip_entity
                        
            cache['route'] = getCachedEntityOr404(Route,id_or_name = trip_entity['route'] )
            cache['agency'] = getCachedEntityOr404(Agency,id_or_name = cache['route']['agency'] )
            
            first = None
            last = None
            try:
                first = db.get(trip.stop_list[0])
                last = db.get(trip.stop_list[len(trip.stop_list)-1])
            except IndexError:
                last = first
            
            stop_entity_list = []
            for key in trip.stop_list:
                stop_id = key.id_or_name()
                try:
                    stop = getCachedEntityOr404(Stop,id_or_name= stop_id)
                    stop_entity_list.append(stop)
                except Http404:
                    logging.error("Stop %s not found" % str(stop_id))
            
            if first != None:
                cache['first'] = createEntity(first)
            else:
                cache['first'] = None
            if last != None:	
                cache['last'] = createEntity(last)
            else:
                cache['last'] = None
            cache['trip'] = trip_entity
            cache['stop_entity_list'] = stop_entity_list
            
            #Fare Trip
            faretrip_entity_list = []
            for faretrip in trip.faretrip_set:
                entity = createEntity(faretrip)
                min = sys.maxint
                max = 0
                for fare in faretrip.fares:
                    if fare < min:
                        min = fare
                    if fare > max:
                        max = fare
                        
                if max > 0 :
                    entity["min_fare"] = min
                    entity["max_fare"] = max
                else:
                    entity["min_fare"] = -1
                    entity["max_fare"] = -1
                    
                faretrip_entity_list.append(entity)
            
            cache['faretrip_entity_list'] = faretrip_entity_list
            
            memcache.add(cache_key, cache, _default_cache_time)

        self.agency = cache['agency']
        self.route = cache['route']
        self.trip  = cache['trip']
            
        # First station/stop	
        self.first = cache['first']
        
        # Last station/stop
        self.last = cache['last']
        self.entity = cache['trip']
        self.stop_entity_list = cache['stop_entity_list']
        self.faretrip_entity_list = cache['faretrip_entity_list']

    def get_agency(self):
        return self.agency
        
    def get_route(self):
        return self.route
        
    def get_trip(self):
        return self.trip
        
    def get_start_end_pair(self):
        """
        Get the start and last station
        """
        return (self.first , self.last)
        
    def get_stop_list(self):
        return self.stop_entity_list
        
    def get_faretrip_list(self):
        return self.faretrip_entity_list
		
class RouteLoader(Loader):
	"""
	Route and related objects loader and cache management
	
	"""

	def __init__(self,id):
		self.id = id_or_name(id)
		self.cache_key_prefix = "gogogo_route_loader_"

	def load(self):
		"""
		Load route and all related objects from memecache or bigtable.
		
		If you only want to load a single entry of Route , please use
		getCachedEntityOr404 instead.
		"""
		
		cache_key = self.get_cache_key()
		
		cache = memcache.get(cache_key)
		
		if cache == None:
			route_entity = getCachedEntityOr404(Route,id_or_name = self.id)
			agency_entity = createEntity(route_entity['instance'].agency)
			
			trip_list = []
			gql = db.GqlQuery("SELECT __key__ from gogogo_trip where route = :1",route_entity['instance'])
			for key in gql:
				id = key.id_or_name()
				trip = TripLoader(id)
				trip.load()
				trip_list.append(trip)
			
			cache = {}	
			cache['route'] = route_entity
			cache['agency'] = agency_entity
			cache['trip_list'] = trip_list
			
			memcache.add(cache_key, cache, _default_cache_time)
			
		self.entity = cache['route']
		self.agency = cache['agency']
		self.trip_list = cache['trip_list']
	
	def get_agency(self):
		return self.agency

	def get_trip_list(self):
		return self.trip_list

################################
# List loader
################################

class ListLoader:
    """
    Load all entity of a model from memcache or bigtable
    """
    
    cache_key_prefix = "gogogo_list_loader_"
    
    def __init__(self,model):
        self.model = model
        self.data = None
        self.cache_key = ListLoader.cache_key_prefix + self.model.kind()
        

    def load(self):
        if self.data != None: #already loaded
            return
            
        cache = memcache.get(self.cache_key)
        
        if cache == None:
            cache = []
            
            query = self.model.all()
            for entry in query:
                cache.append(entry)
                
            memcache.add(self.cache_key, cache, _default_cache_time)
        
        self.data = cache
        
	def remove_cache(self):
		memcache.delete(self.cache_key)
        
    def get_data(self):
        return self.data

class RouteListLoader:
    """
    Load all route into memory from BigTable or memcache
    
    Deprecated
    """
    
    cache_key = "gogogo_route_list"
    
    def __init__(self):
        self.list = None
        
    def load(self):
        if self.list != None: 
            #already loaded
            return
        
        cache = memcache.get(RouteListLoader.cache_key)
		
        if cache == None:
            cache = []
            
            query = Route.all()
            for route in query:
                cache.append(route)
                
            memcache.add(RouteListLoader.cache_key, cache, _default_cache_time)
        
        self.list = cache
        
	def remove_cache(self):
		memcache.delete(RouteListLoader.cache_key)
        
    def get_list(self):
        return self.list
