from django import forms
from django.forms import ModelForm

from gogogo.models import *
from gogogo.models import TitledStringListField
from gogogo.models.MLStringProperty import MLStringProperty , to_key_name
from gogogo.views.widgets import LatLngInputWidget

class StopForm(ModelForm):
    class Meta:
        model = Stop
        
        exclude = ["geohash"]
        
    name = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())
    latlng = forms.CharField(widget = LatLngInputWidget)
    log_message = forms.CharField(widget = forms.Textarea)
