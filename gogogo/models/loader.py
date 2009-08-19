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
from cache import getCachedEntityOr404

from google.appengine.api import memcache
from . import Route , Trip , Stop
from StopList import StopList
import logging

_default_cache_time = 3600

class Loader:
	
	def get_entity(self):
		return self.entity

class TripLoader(Loader):
	"""
	Trip and related object loader and cache management
	
	"""
	def __init__(self,id):
		self.id = id_or_name(id)

	def load(self):
		"""
		Load trip and all related objects from memecache or bigtable.
		
		If you only want to load a single entry of Trip , please use
		getCachedEntityOr404 instead.
		"""
		
		cache_key = "gogogo_trip_loader_%s" % str(self.id)
		
		cache = memcache.get(cache_key)
		
		if cache == None:
			trip_entity = getCachedEntityOr404(Trip,id_or_name = self.id)
			trip = trip_entity['instance']
			
			first = None
			last = None
			try:
				first = db.get(trip.stop_list[0])
				last = db.get(trip.stop_list[len(trip.stop_list)-1])
			except IndexError:
				self.last = self.first
			
			stop_entity_list = []
			for key in trip.stop_list:
				stop_id = key.id_or_name()
				try:
					stop = getCachedEntityOr404(Stop,id_or_name= stop_id)
					stop_entity_list.append(stop)
				except Http404:
					logging.error("Stop %s not found" % str(stop_id))
		
			cache = {}	
			cache['first'] = createEntity(first)
			cache['last'] = createEntity(last)
			cache['trip'] = trip_entity
			cache['stop_entity_list'] = stop_entity_list
			
			memcache.add(cache_key, cache, _default_cache_time)
			
		# First station/stop	
		self.first = cache['first']
		
		# Last station/stop
		self.last = cache['last']
		self.entity = cache['trip']
		self.stop_entity_list = cache['stop_entity_list']
		
class RouteLoader(Loader):
	"""
	Route and related objects loader and cache management
	
	"""

	def __init__(self,id):
		self.id = id_or_name(id)

	def load(self):
		"""
		Load route and all related objects from memecache or bigtable.
		
		If you only want to load a single entry of Route , please use
		getCachedEntityOr404 instead.
		"""
		
		cache_key = "gogogo_route_loader_%s" % str(self.id)
		
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
