# -*- coding: utf-8 -*-
from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from TitledStringListProperty import TitledStringListProperty
from django.utils.translation import ugettext_lazy as _
from ragendja.dbutils import get_object
from geo.geohash import Geohash

class MLStringProperty(TitledStringListProperty):
	"""
		Multi-language string property
	"""
	def __init__ (self,*args,**kwargs):
		fields = []
		for f in settings.LANGUAGES:
			fields.append(f[1])
		
		super(MLStringProperty,self).__init__(fields,*args,**kwargs)
	
class Agency(db.Model):
	"""
		Public transportation agency
	"""
	
	name = MLStringProperty(required=True)
	
	url = db.StringProperty()
	
	timezone = db.StringProperty()
	
	# Don't use PhoneNumberProperty as we allow empty string in upload
	phone = db.StringProperty()
	
	#desc = MLStringProperty() - Later will implement a text input for multiple language handling

	class Meta:
		verbose_name = _('Transport Agency')
		verbose_name_plural = _('Transport Agency')
	
	def __unicode__(self):
		return u' | '.join(self.name)
		
class Stop(db.Model):
	"""
		Stop data
	"""
	agency = db.ReferenceProperty(Agency,required=False)	
	
	# Optional field. A human readable ID for passengers
	code = db.StringProperty()
	
	# name of the Stop (Multiple language)
	name = MLStringProperty(required=True)
	
	desc = MLStringProperty()

	# Geo position of the stop. It is not indexed. Instead, it should use geohash
	latlng = db.GeoPtProperty()
	
	geohash = db.StringProperty()
	
	# TRUE if the geo position data is accuracy enough 
	inaccuracy = db.BooleanProperty()
	
	# URL for the STOP information
	# Link must not be empty. Therefore , we use String Property
	url = db.StringProperty()
	
	# 0  or blank - Stop. A location where passengers board or disembark from a transit vehicle. 
	# 1 - Station. A physical structure or area that contains one or more stop. 
	location_type = db.IntegerProperty(choices=set([0,1]))
	
	parent_station = db.SelfReferenceProperty()

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


class Route(db.Model):	
	class Meta:
		verbose_name = _('Routes')
		verbose_name_plural = _('Routes')

	def __unicode__(self):
		return unicode(self.short_name)

	# An ID assigned by public agency, which is used to identify record in data import
	rid = db.StringProperty(required=True)
	
	agency = db.ReferenceProperty(Agency,required=True)
	
	short_name = db.StringProperty(required=True)
	
	long_name = MLStringProperty()
	
	desc = MLStringProperty()
	
	type = db.IntegerProperty(choices=set(range(0,8)))
	
	#Link must not be empty. Therefore , we use String Property
	url = db.StringProperty()
	
	color = db.StringProperty()
	
	text_color = db.StringProperty()
	
	# List of trips associated to this route
	#trips = KeyListProperty(Trip)

class Trip(db.Model):
	class Meta:
		verbose_name = _('Trips')
		verbose_name_plural = _('Trips')

	route = db.ReferenceProperty(Route)

	#service = db.ReferenceProperty(Service)

	# The trip_id field contains an ID that identifies a trip. The trip_id is dataset unique. 
	tid = db.StringProperty()
	
	headsign = MLStringProperty()
	
	short_name = MLStringProperty()
	
	direction = db.IntegerProperty(choices=set(range(0,2)))
	
	#block - reserved
	
	#shape - reserved	
	
class StopTime(db.Model):
	"""
		Store StopTime information temporary. 
	"""
	
	trip = db.ReferenceProperty(Trip)
	
	# arrival_time = db.TimeProperty()
	
	# departure_time
	stop = db.ReferenceProperty(Stop)
	
	sequence = db.IntegerProperty()
	
	#headsign =  MLStringProperty()
	
	# pickup_type
	
	# drop_off_type
	
	# shape_dist_traveled
	
class Calendar(db.Model):
	class Meta:
		verbose_name = _('Service Calendar')
		verbose_name_plural = _('Service Calendar')
	
	#Service ID
	sid = db.StringProperty()
	
	monday = db.BooleanProperty()
	
	tuesday = db.BooleanProperty()
	wednesday = db.BooleanProperty()
	thursady = db.BooleanProperty()
	
	friday = db.BooleanProperty()
	
	saturday = db.BooleanProperty()

	sunday = db.BooleanProperty()
	
	start_date = db.DateProperty()
	
	end_state = db.DateProperty()
