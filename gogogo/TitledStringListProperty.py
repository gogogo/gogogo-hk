# -*- coding: utf-8 -*-
from google.appengine.ext import db
from django import forms
from django.utils.safestring import mark_safe

class TitledStringListInput(forms.MultiWidget):	

	def __init__(self, fields, attrs=None):
		self.widgets = []
		for lang in fields:
			self.widgets.append(forms.TextInput());
			self.fixed_fields = fields
		super(TitledStringListInput, self).__init__(self.widgets,attrs)	
		
	def decompress(self,value):
		new_value =  [None]
		
		if value:
			if isinstance(value,unicode): #Why it is unicode?
				new_value = value.split('\n')
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

class TitledStringListField(forms.MultiValueField):

	def __init__(self,  *args, **kwargs):
		fields = []
		if "fixed_fields" in kwargs:
			self.fixed_fields = kwargs["fixed_fields"]
			for f in self.fixed_fields:
				fields.append(forms.CharField())
			del kwargs["fixed_fields"]

		kwargs.update( { 'widget' :TitledStringListInput(self.fixed_fields)  })
				
		super(TitledStringListField, self).__init__(fields,*args, **kwargs)

	def compress(self,data_list):
		return data_list
	
class TitledStringListProperty(db.StringListProperty):
	
	def __init__ (self, fields ,*args, **kwargs):
		self.fixed_fields = fields
		db.StringListProperty.__init__(self,*args,**kwargs)

	def get_form_field(self, **kwargs):
		attrs = {
			'form_class': TitledStringListField,
			'fixed_fields' : self.fixed_fields,
        }
		attrs.update(kwargs)
		return super(TitledStringListProperty, self).get_form_field(**attrs)		
		
	def validate(self, value):
		return super(TitledStringListProperty, self).validate(value)
