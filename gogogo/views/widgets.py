from google.appengine.ext import db

from django.core.urlresolvers import reverse
from django import forms
from django.forms.widgets import Input
from django.utils.safestring import mark_safe

from gogogo.models.cache import getCachedObjectOr404
import cgi

class Pathbar:
	"""
	Create a path bar
	
	Template: gogogo/widgets/pathbar.html
	"""
	def __init__(self,sep=">"):
		self.path = []
		self.sep = sep
		
	def append(self,name,viewname,args):
		url = reverse(viewname,args=args)
		self.path.append((name , url ))

		
class ReferenceLinkWidget(Input):
	"""
	Render the link to a database object 
	"""
	
	input_type = 'hidden'
	
	def render(self, name, value, attrs=None):
		
		input = super(ReferenceLinkWidget, self).render(name, value, attrs)	
		
		ret = ""
		if value is not None:
			object = getCachedObjectOr404(key = value)
			ret = mark_safe(input + "<a href='%s'>%s</a>" % (object.get_absolute_url() , unicode(object) ))
		
		return ret

class ReferenceLinkField(forms.Field):	
	"""
	A read-only field with a link to the target of reporting object
	"""

	def __init__(self,  *args, **kwargs):
		
		if 'widget' not in kwargs:
			kwargs.update( { 'widget' : ReferenceLinkWidget() })
				
		super(ReferenceLinkField, self).__init__(*args, **kwargs)

		
	def clean(self,value):
		
		value = super(ReferenceLinkField, self).clean(value)
		if not value:
			return None
		instance = db.get(value)
		if instance is None:
			raise db.BadValueError(self.error_messages['invalid_choice'])
		return instance
