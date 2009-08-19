from django import forms
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe

from django.template import Context, loader , RequestContext
from django.forms.util import flatatt
import logging

class LatLngInputWidget(forms.Widget):
	
	def __init__(self, attrs=None):
		super(LatLngInputWidget, self).__init__(attrs)
	
	def render(self, name, value, attrs=None):
		if value is None: value = ''
		
		final_attrs = self.build_attrs(attrs, name=name)
		if value != '':
			final_attrs['value'] = force_unicode(value)
		
		t = loader.get_template('gogogo/widgets/latlnginputwidget.html')	
		c = Context({
        	'final_attrs': mark_safe(flatatt(final_attrs)),
        	'value' : value,
        	'id' : final_attrs['id'],
        	'map_id' : "map_%s" % final_attrs['id'],
        	'marker_id' : "marker_%s" % final_attrs['id']
    	})
			
		return mark_safe(	t.render(c) )
		
