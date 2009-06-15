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
		Public transportation agency data model
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
		Stop/Station data model
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
	inaccuracy = db.BooleanProperty(default=False)
	
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
	
	agency = db.ReferenceProperty(Agency,required=True)
	
	short_name = db.StringProperty(required=True)
	
	long_name = MLStringProperty()
	
	desc = MLStringProperty()
	
	type = db.IntegerProperty(choices=set(range(0,8)))
	
	#As Link must not be empty, it is replaced by String Property
	url = db.StringProperty()
	
	color = db.StringProperty()
	
	text_color = db.StringProperty()

class Shape(db.Model):
	"""
		Shape data model. The stored data can be a polyline or polygon
		that represent a route, trip and zone etc.
	"""

	# A shape can be a polyline of  polygon
	polygon = db.BooleanProperty(default=False)

	# Color of the shape
	color = db.StringProperty()
	
	# Points of the shape.
	points = db.ListProperty(float)

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

	route = db.ReferenceProperty(Route)

	service = db.ReferenceProperty(Calendar)

	headsign = MLStringProperty()
	
	short_name = MLStringProperty()
	
	direction = db.IntegerProperty(choices=set(range(0,2)))
	
	block = db.StringProperty()
	
	shape = db.ReferenceProperty(Shape)
	
	sequence = KeyListProperty(Stop)
	
class Cluster:
	
	class Meta:
		verbose_name = _('Cluster')
		verbose_name_plural = _('Cluster')

	center = db.GeoPtProperty()
	
	geohash = db.StringProperty()
	
	radius = db.FloatProperty()

	shape = db.ReferenceProperty(Shape)
		
	members = KeyListProperty(Stop)
	
class Changeset(db.Model):
	"""
		Change log
	"""
	
	# The committer. Anonymouse is not allowed
	committer = db.UserProperty()
	
	# Date of submission
	commit_date = db.DateTimeProperty()
	
	# Comment of the submission
	comment = db.TextProperty()
	
	# Additional tag of the log
	tag = db.TextProperty()
	
	# A reference to the modified record.
	reference = db.ReferenceProperty()
	
	# Original data
	old_rev = db.TextProperty()

	# New version of data
	new_rev = db.TextProperty()
