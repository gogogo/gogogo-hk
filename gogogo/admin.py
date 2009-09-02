from django.contrib import admin
from django import forms
from ragendja.forms import *
from gogogo.models import *
from gogogo.models.utils import copyModel
from gogogo.models.forms import *
from gogogo.views.db.forms import next_key_name
from django.conf import settings

class AgencyAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'url',
            'phone',
            'icon',
            'no_service',
            'free_transfer'
            )
        }),

    )
    
    form = AgencyBasicForm

    list_display = ('Agency_ID','Agency_Name','url')	

    search_fields = ('name',)

    def Agency_Name(self,obj):
        return u' | '.join(obj.name)
        
    def Agency_ID(self,obj):
        #return obj.aid
        return obj.key().id_or_name()
        
    def save_model(self,request,obj,form,change):
        if change:
            return admin.ModelAdmin.save_model(self,request,obj,form,change)
        else:            
            new_obj = copyModel(obj,key_name = next_key_name(Agency,Agency.gen_key_name(obj.name)) )
            new_obj.save()

admin.site.register(Agency, AgencyAdmin)

class StopAdmin(admin.ModelAdmin):	
    #fieldsets = (
        #(None, {
            #'fields': (
                #'agency',
                #'code',  
                #'name',
                #'address',
                #'desc',
                #'latlng',
                #'geohash',
                #'url',
                #'location_type',
                #'parent_station',
                #'inaccuracy',
                #)
        #}),
    #)
    
    form = StopBasicForm

    search_fields = ('name',)

    list_display = ('Stop_ID','Stop_Name',)
    
    exclude = ('log_message',)

    change_form_template = "gogogo/admin/change_form.html"

    def Stop_ID(self,obj):
        return obj.key().name()

    def Stop_Name(self,obj):
        return u' | '.join(obj.name)

    def save_model(self,request,obj,form,change):
        if change:
            return admin.ModelAdmin.save_model(self,request,obj,form,change)
        else:            
            new_obj = copyModel(obj,key_name = next_key_name(Stop,Stop.gen_key_name(obj.name)) )
            new_obj.save()

admin.site.register(Stop, StopAdmin)

class RouteAdmin(admin.ModelAdmin):
	fieldsets = (
        (None, {
            'fields': (
     				'agency','short_name','long_name','desc','type','url','color','text_color'
            	)
        }),
    )	
	
admin.site.register(Route, RouteAdmin)

class TripAdmin(admin.ModelAdmin):
	list_display = ('Trip_ID',)	
	
	def Trip_ID(self,obj):
		return obj.key().name()
	
admin.site.register(Trip, TripAdmin)	

class ShapeAdmin(admin.ModelAdmin):
	list_display = ('Shape_ID',)	
	
	def Shape_ID(self,obj):
		return obj.key().id_or_name()
	
admin.site.register(Shape, ShapeAdmin)	

class ClusterAdmin(admin.ModelAdmin):
	list_display = ('Cluster_Name',)
	
	def Cluster_Name(self,obj):
		if obj.station != None:
			return obj.name
		return obj.key().id_or_name()
	
admin.site.register(Cluster, ClusterAdmin)		

class ChangelogAdmin(admin.ModelAdmin):
	fieldsets = (
        (None, {
            'fields': (
     				'committer','commit_date','model_kind','old_rev','new_rev','comment','tag','masked'
            	)
        }),
    )	
	exclude = ('reference',)
	
admin.site.register(Changelog, ChangelogAdmin)	

class ReportAdmin(admin.ModelAdmin):
	pass
	
admin.site.register(Report, ReportAdmin)		

class FareTripAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(FareTrip, FareTripAdmin)

class FareStopAdmin(admin.ModelAdmin):
    list_display = ('FareStop_Name',)

    def FareStop_Name(self,obj):
        agency_id = str(obj.agency.key().id_or_name())
        return "[%s] - %s" % (agency_id , str(obj.key().id_or_name()))
    
    def save_model(self,request,obj,form,change):
        if change:
            return admin.ModelAdmin.save_model(self,request,obj,form,change)
        else:            
            new_obj = copyModel(obj,key_name = next_key_name(FareStop,FareStop.gen_key_name(obj.agency,obj.name)) )
            new_obj.save()
            
    
admin.site.register(FareStop, FareStopAdmin)

class FarePairAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(FarePair, FarePairAdmin)

class TransferAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Transfer, TransferAdmin)
