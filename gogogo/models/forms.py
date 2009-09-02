from django import forms
from django.forms import ModelForm

from gogogo.models import *
from gogogo.models import TitledStringListField
from gogogo.models.MLStringProperty import MLStringProperty , to_key_name
from gogogo.views.widgets import LatLngInputWidget , StopListEditor

class AgencyBasicForm(ModelForm):
    class Meta:
        model = Agency
        fields = ["name"]
        
    url = forms.CharField(required=False)
    phone = forms.CharField(required=False)
    icon = forms.CharField(required=False)
    no_service = forms.BooleanField(required=False)
    free_transfer = forms.BooleanField(required=False)
    
class AgencyForm(AgencyBasicForm):
    log_message = forms.CharField(widget = forms.Textarea)

class StopBasicForm(ModelForm):
    class Meta:
        model = Stop
        
        exclude = ["geohash"]
        
    name = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())
    latlng = forms.CharField(widget = LatLngInputWidget)


class StopForm(StopBasicForm):
    log_message = forms.CharField(widget = forms.Textarea)

class TripBasicForm(ModelForm):
    class Meta:
        model = Trip
        
        #TODO - Reenable stop_list
        fields = ["headsign"]
        #exclude = ["stop_list"]

    headsign = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())	
    
    stop_list = forms.CharField(widget = StopListEditor)

class TripForm(TripBasicForm):
    log_message = forms.CharField(widget = forms.Textarea)
