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

    def validate(self, value):
        if isinstance(value,basestring):
            value = int(value)
        
        return super(TransitTypeProperty, self).validate(value)
        
    def get_form_field(self, **kwargs):
        attrs = {
            'form_class': forms.ChoiceField,
            'choices' : TransitTypeProperty.get_choices()
        }
        attrs.update(kwargs)
        return super(TransitTypeProperty, self).get_form_field(**attrs)		
        
    def get_choices():
        ret = [ (i,TransitTypeProperty.get_type_name(i)) for i in range(0,8)]
        
        return ret
    
    get_choices = staticmethod(get_choices)
        
    def get_basic_type_name_list():
        """
        Return a list of basic type name
        """
        ret = [TransitTypeProperty.get_type_name(i) for i in range(0,8)]
        
        return ret
        
    get_basic_type_name_list = staticmethod(get_basic_type_name_list)   

    def get_type_name(type):
        if type == 0:
            return _("Tram, Streetcar, Light rail")
        elif type == 1:
            return _("Subway, Metro") #Any underground rail system within a metropolitan area
        elif type == 2:
            return _("Rail") #Used for intercity or long-distance travel. 
        elif type == 3:
            return _("Bus")
        elif type == 4:
            return _("Ferry")
        elif type == 5:
            return _("Cable car")
        elif type == 6:
            return _("Gondola, Suspended cable car")
        elif type == 7:
            return _("Funicular")
        else:
            return ""
            
    get_type_name = staticmethod(get_type_name)


class PaymentMethodProperty(db.IntegerProperty):
    """
    Payment Method
    """
    def __init__ (self,*args,**kwargs):    
        kwargs["choices"] = range(0,2)
        if "default" not in kwargs:
            kwargs["default"] = 0
        db.IntegerProperty.__init__(self,*args,**kwargs)

    def validate(self, value):
        if isinstance(value,basestring):
            value = int(value)
        
        return super(PaymentMethodProperty, self).validate(value)
        
    def get_form_field(self, **kwargs):
        attrs = {
            'form_class': forms.ChoiceField,
            'choices' : PaymentMethodProperty.get_choices()
        }
        attrs.update(kwargs)
        return super(PaymentMethodProperty, self).get_form_field(**attrs)		
        
    def get_choices():
        ret = [ (i,PaymentMethodProperty.get_type_name(i)) for i in range(0,2)]
        
        return ret
        
    get_choices = staticmethod(get_choices)

    def get_type_name(type):
        if type == 0:
            return _("Fare is paid on board")
        elif type == 1:
            return _("Fare must be paid before boarding")
            
    get_type_name = staticmethod(get_type_name)
