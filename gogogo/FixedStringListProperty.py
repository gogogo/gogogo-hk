# -*- coding: utf-8 -*-
from google.appengine.ext import db
from django import forms
from django.utils.safestring import mark_safe

class FixedStringListInput(forms.MultiWidget):	

	def __init__(self, fields, attrs=None):
		self.widgets = []
		for lang in fields:
			self.widgets.append(forms.TextInput());
			self.fixed_fields = fields
		super(FixedStringListInput, self).__init__(self.widgets,attrs)	
		
	def decompress(self,value):
		new_value =  [None]
		
		if value:
			if isinstance(value,unicode):
				new_value = value.split(',')
			else:
				new_value = value
		return new_value
		
	def format_output(self, rendered_widgets):
		output = []
	
		for i,field in enumerate(self.fixed_fields):
			output.append(u'<div>%s</div>' % field)
			output.append(rendered_widgets[i])
		
		HTML = "<div style='display : block;float : left'> %s </div>"	 %  u''.join(output)
		
		return HTML

class FixedStringListField(forms.MultiValueField):

	def __init__(self,  *args, **kwargs):
		fields = []
		if "fixed_fields" in kwargs:
			self.fixed_fields = kwargs["fixed_fields"]
			for f in self.fixed_fields:
				fields.append(forms.CharField())
			del kwargs["fixed_fields"]

		kwargs.update( { 'widget' :FixedStringListInput(self.fixed_fields)  })
				
		super(FixedStringListField, self).__init__(fields,*args, **kwargs)

	def compress(self,data_list):
		return data_list
	
class FixedStringListProperty(db.StringListProperty):
	
	def __init__ (self, fields ,*args, **kwargs):
		self.fixed_fields = fields
		db.StringListProperty.__init__(self,*args,**kwargs)

	def get_form_field(self, **kwargs):
		attrs = {
			'form_class': FixedStringListField,
			'fixed_fields' : self.fixed_fields,
			'required': False
        }
		attrs.update(kwargs)
		return super(FixedStringListProperty, self).get_form_field(**attrs)		
		
	def validate(self, value):
		return super(FixedStringListProperty, self).validate(value)
