from django.contrib import admin
from django import forms

from gogogo.models import Agency

class AgencyAdminForm(forms.ModelForm):
	class Meta:
		model = Agency
		
	name = forms.CharField(max_length=100)
	

class AgencyAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'timezone', 'phone')
        }),

    )
    
    list_display = ('name','url')	
    
    #form = AgencyAdminForm


admin.site.register(Agency, AgencyAdmin)

