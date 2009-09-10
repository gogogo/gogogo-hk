from google.appengine.ext import db

from django.core.urlresolvers import reverse
from django import forms
from django.forms.widgets import Input
from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.template import Context, loader , RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.http import Http404

from gogogo.models.cache import getCachedObjectOr404
from gogogo.models.utils import id_or_name
from gogogo.models import Stop
import cgi
import logging

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
	Render the link to a database object(Use with ReferenceLinkField)
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

class SimpleReferenceWidget(Input):
    
    def __init__(self,*args,**kwargs):
        self.___model_class = kwargs['model_class']
        del kwargs['model_class']
        
        super(SimpleReferenceWidget,self).__init__(*args,**kwargs)
    
    def render(self, name, value, attrs=None):
        
        object = None
        try:
            object = getCachedObjectOr404(self.___model_class,key = value)
        except Http404:
            pass
        
        if isinstance(value,db.Key):
            value = value.id_or_name()
        
        input = super(SimpleReferenceWidget, self).render(name, value, attrs)	
        ret = input
        if object:
            ret = mark_safe(input + " <a href='%s'>%s</a>" % (object.get_absolute_url() , unicode(object) ))
        
        return ret

class SimpleReferenceField(forms.Field):
    """
    A write-read field of ReferenceProperty which have a simple text box for entry 
    the ID directly. 
    """

    def __init__(self,  *args, **kwargs):
        
        self.___model_class = kwargs['model_class']
        del kwargs['model_class']
        
        if 'widget' not in kwargs:
            kwargs.update( { 'widget' : SimpleReferenceWidget(model_class =self.___model_class  ) })
        
                
        super(SimpleReferenceField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        final_value = None
        if self.required and not value:
            raise forms.ValidationError(_(u'This field is required.'))
        elif not self.required and not value:
            return None
                        
        if isinstance(value,basestring):
            id = id_or_name(value)
            final_value = db.Key.from_path(self.___model_class.kind(),id)

        try:
            object = getCachedObjectOr404(self.___model_class,key = final_value)
        except Http404:
            raise forms.ValidationError(_(u'This record not found.'))            
        
        return final_value

class LatLngInputWidget(forms.Widget):	
    def __init__(self, attrs=None):
        super(LatLngInputWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None: value = "%s,%s" % (settings.GOGOGO_DEFAULT_LOCATION[0],settings.GOGOGO_DEFAULT_LOCATION[1])
        
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            final_attrs['value'] = force_unicode(value)
        
        t = loader.get_template('gogogo/widgets/latlnginputwidget.html')	
        c = Context({
            'final_attrs': mark_safe(flatatt(final_attrs)),
            'value' : value,
            'id' : final_attrs['id'],
            'map_id' : "map_%s" % final_attrs['id'],
            'model_manager' : "model_manager_%s" % final_attrs['id'],
            'cluster_manager' : "cluster_manager_%s" % final_attrs['id'],
            'marker_id' : "marker_%s" % final_attrs['id']
        })
            
        return mark_safe(	t.render(c) )

class StopListEditor(forms.Widget):
    """
    Stop list editor
    """

    def render(self, name, value, attrs=None):
        if value is None: value = "%s,%s" % (settings.GOGOGO_DEFAULT_LOCATION[0],settings.GOGOGO_DEFAULT_LOCATION[1])
        
        final_attrs = self.build_attrs(attrs, name=name)
        if value != '':
            final_attrs['value'] = force_unicode(self._gen_value(value))
        
        t = loader.get_template('gogogo/widgets/stoplisteditor.html')	
        c = Context({
            'final_attrs': mark_safe(flatatt(final_attrs)),
            'value' : value,
            'id' : final_attrs['id'],
            'map_id' : "map_%s" % final_attrs['id'],
            'editor' : "editor_%s" % final_attrs['id'],
            'sortable_id' : "sortable_%s" % final_attrs['id'],
        })
            
        return mark_safe(	t.render(c) )
    
    def _gen_value(self,value):
        ret = []
        for v in value:
            if isinstance(v,basestring):                
                ret.append(v)
            else:
                ret.append(str(v.id_or_name()))
        return ",".join(ret)
        
class StopListField(forms.Field):

    def __init__(self,  *args, **kwargs):
        
        if 'widget' not in kwargs:
            kwargs.update( { 'widget' : StopListEditor() })
                
        super(StopListField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if self.required and not value:
            raise forms.ValidationError(_(u'This field is required.'))
        elif not self.required and not value:
            return []
        if isinstance(value,basestring):
            value = value.split(",")
            
        if not isinstance(value, (list, tuple)):
            raise ValidationError(gettext(u'Enter a list of values.'))
        
        final_values = []
        for val in value:
            key = db.Key.from_path(Stop.kind(),id_or_name(val))
            final_values.append(key)
        return final_values
