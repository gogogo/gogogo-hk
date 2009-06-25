from google.appengine.ext import db
from django import forms

class NumberListProperty(db.ListProperty):
	
	def get_value_for_form(self, instance):
		"""Extract the property value from the instance for use in a form.
		"""

		value = super(NumberListProperty, self).get_value_for_form(instance)
		if not value:
			return None
		if isinstance(value, list):
			value = ','.join([str(v) for v in value])
		return value

	def make_value_from_form(self, value):
		"""Convert a form value to a property value.

		This breaks the string into lines.
		"""
		if not value:
			return []
		if isinstance(value, basestring):
			value = [ self.item_type(v) for v in value.split(',')]
			
		return value
