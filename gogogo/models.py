# -*- coding: utf-8 -*-
from google.appengine.ext import db
from ragendja.dbutils import KeyListProperty
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

class MultiLangStringInput(forms.MultiWidget):	

	def __init__(self, attrs=None):
		self.widgets = []
		for lang in settings.LANGUAGES:
			self.widgets.append(forms.TextInput());
		super(MultiLangStringInput, self).__init__(self.widgets,attrs)	
		
	def decompress(self,value):
		new_value =  [None] * len(settings.LANGUAGES)
		
		if value:
			if isinstance(value,unicode):
				new_value = value.split()
			else:
				new_value = value
		return new_value

	def format_output(self, rendered_widgets):
		output = []
	
		for i,lang in enumerate(settings.LANGUAGES):
			output.append(u'<div>%s</div>' % lang[1])
			output.append(rendered_widgets[i])
		
		HTML = "<div style='display : block;float : left'> %s </div>"	 %  u''.join(output)
		
		return HTML

class MultiLangStringField(forms.MultiValueField):

	def __init__(self, *args, **kwargs):
		fields = []
		
		for lang in settings.LANGUAGES:
			fields.append(forms.CharField())

		kwargs.update( { 'widget' :MultiLangStringInput  })
				
		super(MultiLangStringField, self).__init__(fields, *args, **kwargs)

	def clean(self,value):
		import logging
		logging.debug("MultiLangStringField::clean")
		
		if not value:
			return []
		
		logging.debug(value)
		return value
		
	
class MultiLangStringProperty(db.StringListProperty):
	"""
		Property to hold multiple language string
	"""
	def __init__ (self, *args, **kwargs):
		db.StringListProperty.__init__(self,*args,**kwargs)

	def get_form_field(self, **kwargs):
		attrs = {
			'form_class': MultiLangStringField,
			'required': True
        }
		attrs.update(kwargs)
		return super(MultiLangStringProperty, self).get_form_field(**attrs)		
		
	def validate(self, value):
		import logging
		logging.debug("MultiLangStringProperty::validate ")
		if value:
			logging.debug(value)

		return super(MultiLangStringProperty, self).validate(value)

class Agency(db.Model):
	"""
		Public transportation agency
	"""
	name = MultiLangStringProperty()
	
	url = db.StringProperty()
	
	timezone = db.StringProperty()
	
	phone = db.PhoneNumberProperty()
	

class Stops(db.Model):
	# An ID that uniquely identifies a stop or station. Multiple routes may use the same stop. 
	sid = db.StringProperty()
	
	# Optional field
	code = db.StringProperty()
	
	# name of the Stop (Multiple language)
	name = db.StringListProperty()
	
	desc = db.StringListProperty()

	# latitude and longitude value, it won't use the indexing function from BigTable. Use geohash instead
	latlng = db.GeoPtProperty()
	
	geohash = db.StringProperty()
	
	# TRUE if the geo position data is accuracy enough 
	accuracy = db.BooleanProperty()
	
	url = db.LinkProperty()
	
	location_type = db.IntegerProperty()
	
	parent_station = db.SelfReferenceProperty()
	
class Routes(db.Model):	
	rid = db.StringProperty()
	
	#agency = db.ReferenceProperty(agency)
	
	short_name = db.StringListProperty()
	
	long_name = db.StringListProperty()
	
	desc = db.StringListProperty()
	
	type = db.IntegerProperty()
	
	url = db.LinkProperty()
	
	color = db.StringProperty()
	
	text_color = db.StringProperty()
