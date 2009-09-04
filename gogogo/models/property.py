from google.appengine.ext import db
from django import forms
from django.utils.translation import ugettext_lazy as _

class TransitTypeProperty(db.IntegerProperty):
    """
    Transit Type Property - Storage of transit type
    """
    def __init__ (self,*args,**kwargs):    
        kwargs["choices"] = range(0,8)
        db.IntegerProperty.__init__(self,*args,**kwargs)
        
    def get_form_field(self, **kwargs):
        attrs = {
            'form_class': forms.ChoiceField,
            'choices' : TransitTypeProperty.get_choices()
        }
        attrs.update(kwargs)
        return super(TransitTypeProperty, self).get_form_field(**attrs)		
        
    def get_choices():
        ret = [ (i,_(TransitTypeProperty.get_type_name(i))) for i in range(0,8)]
        
        return ret
        
    get_choices = staticmethod(get_choices)

    def get_type_name(type):
        if type == 0:
            return "Tram, Streetcar, Light rail"
        elif type == 1:
            return "Subway, Metro" #Any underground rail system within a metropolitan area
        elif type == 2:
            return "Rail" #Used for intercity or long-distance travel. 
        elif type == 3:
            return "Bus"
        elif type == 4:
            return "Ferry"
        elif type == 5:
            return "Cable car"
        elif type == 6:
            return "Gondola, Suspended cable car"
        elif type == 7:
            return "Funicular"
            
    get_type_name = staticmethod(get_type_name)
