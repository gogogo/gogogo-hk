# -*- coding: utf-8 -*-
from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
from TitledStringListProperty import TitledStringListProperty
from django.utils.translation import ugettext_lazy as _

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
	
	phone = db.PhoneNumberProperty()
	
	#desc = MLStringProperty() - Later will implement a text input for multiple language handling

	class Meta:
		verbose_name = _('Transport Agency')
		verbose_name_plural = _('Transport Agency')
	
	def __unicode__(self):
		return u' | '.join(self.name)
		
class Stop(db.Model):
	class Meta:
		verbose_name = _('Stops')
		verbose_name_plural = _('Stops')

	def __unicode__(self):
		return u' | '.join(self.name)
	
	# An ID that uniquely identifies a stop or station. Multiple routes may use the same stop. 
	sid = db.StringProperty()
	
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
	url = db.LinkProperty()
	
	# 0  or blank - Stop. A location where passengers board or disembark from a transit vehicle. 
	# 1 - Station. A physical structure or area that contains one or more stop. 
	location_type = db.IntegerProperty(choices=set([0,1]))
	
	parent_station = db.SelfReferenceProperty()
	
	agency = db.ReferenceProperty(Agency,required=True)
	
	# Trips that use this STOP
	# trips = 	
	
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
	
	url = db.LinkProperty()
	
	color = db.StringProperty()
	
	text_color = db.StringProperty()

class Trip(db.Model):
	class Meta:
		verbose_name = _('Trips')
		verbose_name_plural = _('Trips')

	# ID of the trip. Used in data import
	tid = db.StringProperty()
	
	route = db.ReferenceProperty(Route)
	
	#service = db.ReferenceProperty(Service)
	
	headsign = MLStringProperty()
	
	short_name = MLStringProperty()
	
	direction = db.IntegerProperty(choices=set(range(0,2)))
	
	
	
