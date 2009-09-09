from django import forms
from django.forms import ModelForm

from gogogo.models import *
from gogogo.models import TitledStringListField
from gogogo.models.MLStringProperty import MLStringProperty , to_key_name
from gogogo.views.widgets import LatLngInputWidget , StopListEditor , StopListField

class AgencyBasicForm(ModelForm):
    class Meta:
        model = Agency
        fields = ["name","type","url","phone","icon","priority","no_service","free_transfer","show_map_in_transit_page"]

    name = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())
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

class RouteBasicForm(ModelForm):
    class Meta:
        model = Route
        fields = ['agency','short_name','long_name','desc','type','url','color','text_color']

    short_name = forms.CharField(required = True)
    long_name = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())

class RouteForm(RouteBasicForm):
    log_message = forms.CharField(widget = forms.Textarea)

class TripBasicForm(ModelForm):
    class Meta:
        model = Trip
        exclude = ["arrival_time_list"]
        
    headsign = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())	
    
    stop_list = StopListField()

class TripForm(TripBasicForm):
    log_message = forms.CharField(widget = forms.Textarea)

class FareTripBasicForm(ModelForm):
    class Meta:
        model = FareTrip
       
        
class FareTripForm(FareTripBasicForm):
    log_message = forms.CharField(widget = forms.Textarea)
