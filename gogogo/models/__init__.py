# -*- coding: utf-8 -*-
from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from TitledStringListProperty import TitledStringListProperty
from django.utils.translation import ugettext_lazy as _
from ragendja.dbutils import get_object
from django.conf import settings

from gogogo.geo.geohash import Geohash

from gogogo.models.NumberListProperty import NumberListProperty

from django.db.models import permalink # For permalink

from utils import createEntity , trEntity
from MLStringProperty import MLStringProperty , to_key_name
# Utilities
from TitledStringListProperty import TitledStringListField

import logging
        
def create_entity(model,request = None):
	""" Create entity (a dict object) from model with: MLString translated. (based on Models._to_entity(self, entity) )

    Deprecated function. Please use createEntity.
	"""
	entity = {}
	code_index = -1
	
	for prop in model.properties().values():
		datastore_value = prop.get_value_for_datastore(model)
		if not datastore_value == []:
			entity[prop.name] = datastore_value
			
			if request and isinstance(prop,MLStringProperty):
				if code_index < 0 and request != None:
					for (i,lang) in enumerate(settings.LANGUAGES):
						if lang[0] == request.LANGUAGE_CODE:
							code_index = i
							break
				
				entity[prop.name] = MLStringProperty.trans(datastore_value,code_index)
				#entity[prop.name] = datastore_value[0]

	return entity

# Database Model
	
class Agency(db.Model):
    """
        Public transportation agency data model
    """

    name = MLStringProperty(required=True)

    url = db.StringProperty(default="")

    timezone = db.StringProperty()

    # Don't use PhoneNumberProperty as we allow empty string in upload
    phone = db.StringProperty()

    #desc = MLStringProperty() - Later will implement a text input for multiple language handling

    icon = db.StringProperty()

    # An agency with "no_service" means that the agency do not provide
    # any transportation service. It is just used to manage facilities
    # (stop) on map.
    no_service = db.BooleanProperty(default=False)

    # A "free_transfer" agency means that passengers are free to transfer
    # from a trip to another trip within the stop. It also imply that
    # the fare is depended on station pairs, how passenger get there doesn't
    # matter
    free_transfer = db.BooleanProperty(default=False)

    class Meta:
        verbose_name = _('Transport Agency')
        verbose_name_plural = _('Transport Agency')

    def __unicode__(self):
        return u' | '.join(self.name)
        
    @permalink
    def get_absolute_url(self):
        return ('gogogo.views.transit.agency',[self.key().id_or_name()]) 
        
    def gen_key_name(obj = None,name = None):
        if obj:
            name = obj.name
        return MLStringProperty.to_key_name(name)
        
    gen_key_name = staticmethod(gen_key_name)
		
class Stop(db.Model):
    """
        Stop/Station data model
    """
    agency = db.ReferenceProperty(Agency,required=False)	

    # Optional field. A human readable ID for passengers
    code = db.StringProperty()

    # name of the Stop (Multiple language)
    name = MLStringProperty(required=True)

    desc = MLStringProperty()

    # The address of the stop
    address = MLStringProperty()

    # Geo position of the stop. It is not indexed. Instead, it should use geohash
    latlng = db.GeoPtProperty()

    geohash = db.StringProperty()

    # TRUE if the geo position data is accuracy enough 
    inaccuracy = db.BooleanProperty(default=False)

    # URL for the STOP information
    # Link must not be empty. Therefore , we use String Property
    url = db.StringProperty()

    # 0  or blank - Stop. A location where passengers board or disembark from a transit vehicle. 
    # 1 - Station. A physical structure or area that contains one or more stop. 
    location_type = db.IntegerProperty(choices=set([0,1]))

    parent_station = db.SelfReferenceProperty()

    # Tag of the stop for advanced feature.
    # e.g Stop with facility for disabled person
    tags = db.StringProperty()

    # nearby stop list
    #near = KeyListProperty(Stop)

    def __init__(self,*args , **kwargs):
        super(Stop,self).__init__(*args,**kwargs)
        
        if "lat" in kwargs and "lng" in kwargs:
            self.latlng = db.GeoPt(kwargs['lat'],kwargs['lng'])
            self.update_geohash()

    class Meta:
        verbose_name = _('Stops')
        verbose_name_plural = _('Stops')

    def __unicode__(self):
        return u' | '.join(self.name)

    def update_geohash(self):
        self.geohash = str(Geohash( (self.latlng.lon , self.latlng.lat) ))

    @permalink
    def get_absolute_url(self):
        return ('gogogo.views.transit.stop',[self.key().id_or_name()]) 
        
    def gen_key_name(obj = None , name = None):
        if obj:
            name = obj.name
        return MLStringProperty.to_key_name(name)
        
    gen_key_name = staticmethod(gen_key_name)

class Route(db.Model):	
	class Meta:
		verbose_name = _('Routes')
		verbose_name_plural = _('Routes')
	
	agency = db.ReferenceProperty(Agency,required=True)
	
	short_name = db.StringProperty()
	
	long_name = MLStringProperty()
	
	desc = db.TextProperty()
	
	# Reference : 
	# http://code.google.com/intl/zh-TW/transit/spec/transit_feed_specification.html#routes_txt___Field_Definitions
	type = db.IntegerProperty(choices=range(0,8))
	
	#As Link must not be empty, it is replaced by String Property
	url = db.StringProperty()
	
	color = db.StringProperty()
	
	text_color = db.StringProperty()

	def __unicode__(self):
		return unicode(self.short_name)

	@permalink
	def get_absolute_url(self):
		return ('gogogo.views.transit.route',[self.agency.key().id_or_name(),self.key().id_or_name()]) 
		
	def get_type_name(type):
		if type == 0:
			return "Tram, Streetcar, Light rail"
		elif type == 1:
			return "Subway, Metro" #Any underground rail system within a metropolitan area
		elif type == 2:
			return "Rail" #Used for intercity or long-distance travel. 
		elif type == 3:
			return "Bus"
		elif type == 4:
			return "Ferry"
		elif type == 5:
			return "Cable car"
		elif type == 6:
			return "Gondola, Suspended cable car"
		elif type == 7:
			return "Funicular"
			
	get_type_name = staticmethod(get_type_name)
	
	def get_choices(cls):
		ret = []
		for i in range(0,8):
			ret.append( (i,cls.get_type_name(i)) )
		return ret
	get_choices = classmethod(get_choices)

class Shape(db.Model):
	"""
		Shape data model. The stored data can be a polyline or polygon
		that represent a route, trip and zone etc.
	"""
	
	def __unicode__(self):
		return unicode(self.key().name())
		
	@permalink
	def get_absolute_url(self):
		return ('gogogo.views.db.shape.browse',[self.key().id_or_name()]) 
		
	def set_owner(self,owner):
		self.owner = owner;
		self.owner_kind = owner.kind()

	# Type of shape. 0: Polyline , 1 : Polygon
	type = db.IntegerProperty()

	# Color of the shape
	color = db.StringProperty()
	
	# Points of the shape.
	points = NumberListProperty(float)
	
	# The owner of the shape
	owner = db.ReferenceProperty()
	
	# The kind of owner entry
	owner_kind = db.StringProperty()

class Calendar(db.Model):
	class Meta:
		verbose_name = _('Service Calendar')
		verbose_name_plural = _('Service Calendar')	
	
	monday = db.StringProperty()
	
	tuesday = db.StringProperty()
	
	wednesday = db.StringProperty()
	
	thursady = db.StringProperty()
	
	friday = db.StringProperty()
	
	saturday = db.StringProperty()

	sunday = db.StringProperty()
	
	holiday = db.StringProperty()
	
	special = db.StringProperty()
	
	special_remark = MLStringProperty()

class Trip(db.Model):
	class Meta:
		verbose_name = _('Trips')
		verbose_name_plural = _('Trips')

	def __unicode__(self):
		return unicode(self.key().id_or_name())

	route = db.ReferenceProperty(Route)

	service = db.ReferenceProperty(Calendar)

	headsign = MLStringProperty()
	
	short_name = MLStringProperty()
	
	direction = db.IntegerProperty(choices=set(range(0,2)))
	
	block = db.StringProperty()
	
	shape = db.ReferenceProperty(Shape)
	
	stop_list = KeyListProperty(Stop)
	
	arrival_time_list = NumberListProperty(int)
	
	@permalink
	def get_absolute_url(self):
		return ('gogogo.views.transit.trip',[self.route.agency.key().id_or_name(),
			self.route.key().id_or_name(),
			self.key().id_or_name()]) 
	
class Cluster(db.Model):
	
	class Meta:
		verbose_name = _('Cluster')
		verbose_name_plural = _('Cluster')

	# The center point of the cluster
	center = db.GeoPtProperty()
	
	# The "station" of the cluster. If this field is set, the center 
	# will always be equal to the location of the station
	station = db.ReferenceProperty(Stop)
	
	# Name of the cluster. If station is set , it will be equal to 
	# the name of the stop
	name = db.StringProperty()
	
	geohash = db.StringProperty()
	
	# The radious of the cluster (in KM)
	radius = db.FloatProperty()

	# The shape of the cluster
	shape = db.ReferenceProperty(Shape)
	
	# Member in the cluster
	members = KeyListProperty(Stop)
	
	def update_geohash(self):
		self.geohash = str(Geohash( (self.center.lon , self.center.lat) ))
		
	def set_station(self,station):
		self.station = station
		if station != None:
			self.center = db.GeoPt(station.latlng.lat,station.latlng.lon)
			self.name = u'|'.join(station.name)
		
class Changelog(db.Model):
	"""
	Record the changes of data modified by web interface
	"""
				
	# The committer. Anonymouse is not allowed
	committer = db.UserProperty(auto_current_user_add=True)
	
	# Date of submission
	commit_date = db.DateTimeProperty(auto_now_add=True)
	
	# Comment of the submission
	comment = db.TextProperty()
	
	# Type of change. 0 = update , 1 = add , 2 = remove
	type = db.IntegerProperty(default=0)
	
	# Additional tag of the log
	tag = db.TextProperty()
	
	# A reference to the modified record.
	reference = db.ReferenceProperty()
	
	# The model kind
	model_kind = db.StringProperty()
	
	# The changes in JSON format produced by diffModel()
	changes = db.TextProperty()
	
	# A masked changelog will not be shown to public. It is probably a spam or invalid commit
	masked = db.BooleanProperty()

	def __unicode__(self):
		return "%s %s %s" % (self.commit_date.isoformat() ,str(self.committer) , self.model_kind )

	def get_type_name(type):
		"""
		Get the name of a type
		"""
		if type == 0:
			return "update"
		elif type == 1:
			return "add"
		elif type =="2":
			return "remove"
		else:
			return "Unknown"
	
	get_type_name = staticmethod(get_type_name)


class Report(db.Model):
	"""
	Report of invalid information
	"""
	
	# The committer. Anonymouse is not allowed
	committer = db.UserProperty(auto_current_user_add=True)

	commit_date = db.DateTimeProperty(auto_now_add=True)

	# The record with problem
	reference = db.ReferenceProperty()
	
	# Subject line of the message
	subject = db.StringProperty()
	
	# Detail of the problem
	detail = db.TextProperty()
	
	# Status of the message. 
	# 0 : Pending , no action has been made
	# 1 : Accepted , will action on the report
	# 2 : Rejected, will not do anything on it
	# 3 : Spam , it is spam
	# 4 : Fixed , it is fixed.
	status = db.IntegerProperty(default=0)

class FareTrip(db.Model):
    """
    The fare of a trip
    """
    # Reference to the trip
    trip = db.ReferenceProperty(Trip)
    
    # The name of the fare type
    name = MLStringProperty()
    
    # TRUE if it is the default fare type used in shortest path calculation
    default = db.BooleanProperty(default = False)

 
    #The payment_method field indicates when the fare must be paid. 
    # Valid values for this field are:
    # 0 - Fare is paid on board.
    # 1 - Fare must be paid before boarding.
    payment_method = db.IntegerProperty(default = 0 ,choices=set([0,1]))
    
    fares = NumberListProperty(float)

class FareStop(db.Model):
    """
    For fare depends on station pairs, how passengers get there doesn't matter.    
    """
    
    agency = db.ReferenceProperty(Agency,required=True)
    
    # The name of the fare type
    name = MLStringProperty(required=True)
    
    # TRUE if it is the default fare type used in shortest path calculation
    default = db.BooleanProperty(default = False)
    
    def gen_key_name(object , agency = None , name = None):
        """
       Generate a key name
       
       @tyep agency db.Key
        """
        if object:
            property = getattr(FareStop, "agency")
            agency = property.get_value_for_datastore(object)            
            name = object.name          
            
        prefix = str(agency.id_or_name())
        
        return prefix + "-" + MLStringProperty.to_key_name(name)
        
    gen_key_name = staticmethod(gen_key_name)
        
    def __unicode__(self):
        if not self.is_saved():
            return u"|".join(self.name)
        return unicode(self.key().id_or_name())

class FarePair(db.Model):
    owner = db.ReferenceProperty(FareStop,collection_name="pair")

    # Start stop
    from_stop = db.ReferenceProperty(Stop,collection_name="fair_pair_from")
    
    # End point stop list
    to_stop = db.ReferenceProperty(Stop,collection_name="fair_pair_to")
    
    fare = db.FloatProperty(default = 0.0)

    def gen_key_name(obj= None , owner = None,from_stop = None,to_stop = None):
        """
       Generate a key name
        """
        
        if obj:
            property = getattr(FarePair, "owner")
            owner = property.get_value_for_datastore(obj)

            property = getattr(FarePair, "from_stop")
            from_stop = property.get_value_for_datastore(obj)

            property = getattr(FarePair, "to_stop")
            to_stop = property.get_value_for_datastore(obj)
        
        if isinstance(owner,db.Key):
            prefix = str(owner.id_or_name())
        else:
            prefix = str(agency.key().id_or_name())
            
        if isinstance(from_stop,db.Key):
            from_stop_str = str(from_stop.id_or_name())
        else:
            from_stop_str = str(from_stop.key().id_or_name())
            
        if isinstance(to_stop,db.Key):
            to_stop_str = str(to_stop.id_or_name())
        else:
            to_stop_str = str(to_stop.key().id_or_name())
        
        return to_key_name(prefix + "-" + from_stop_str + "-to-" + to_stop_str)
        
    gen_key_name = staticmethod(gen_key_name)
    
    def __unicode__(self):
		return unicode(self.key().id_or_name())

class Transfer(db.Model):
    """
    For agency with free transfer service, there may have 2 stations
    that is connected and allow passengers to changes their trip freely.
    
    If such service is existed, it should record the station pair in this 
    model.
    """
    
    agency = db.ReferenceProperty(Agency)
    
    from_stop = db.ReferenceProperty(Stop,collection_name="transfer_from_stop")
    
    to_stop = db.ReferenceProperty(Stop,collection_name="transfer_to_stop")
    
    max_transfer_time = db.IntegerProperty(default=-1)
    
