
###################################################################
# Database frontend (for advanced data viewing and editing)
###################################################################

from gogogo.models import *
from ragendja.auth.decorators import staff_only
from ragendja.dbutils import get_object_or_404
from django import forms
from django.forms import ModelForm
from ragendja.template import render_to_response

from django.core.urlresolvers import reverse as _reverse
from gogogo.models.utils import createEntity , entityToText
from gogogo.models.cache import updateCachedObject
from datetime import datetime

#def reverse(object):
	#"""
	#Return the link to the object
	#"""
	
	#if isinstance(object,Agency):
		#ret = _reverse('gogogo.views.transit.agency',args=[object.key().name()] )
	#elif isinstance(object,Route):
		#ret = _reverse('gogogo.views.transit.route',args=[object.agency.key().name(),object.key().name()] )
	#elif isinstance(object,Trip):
		#ret = _reverse('gogogo.views.transit.trip',args=[object.route.agency.key().name(),
			#object.route.key().name(),
			#object.key().name()] )
	#else:
		#raise ValueError("gogogo.views.db.reverse() do not support %s" % object.kind() )	

	#return ret

class AgencyForm(ModelForm):
	class Meta:
		model = Agency
		fields = ['name','phone','url','icon']
		
	log_message = forms.CharField(widget = forms.Textarea)

class RouteForm(ModelForm):
	class Meta:
		model = Route
		fields = ['agency','short_name','long_name','desc','type','url','color','text_color']
		
	log_message = forms.CharField(widget = forms.Textarea)

class TripForm(ModelForm):
	class Meta:
		model = Trip
		exclude = ["stop_list"]
		
	log_message = forms.CharField(widget = forms.Textarea)

_supported_model = {
	'route' : (Route,RouteForm),
	'agency' : (Agency,AgencyForm),
	'trip' : (Trip,TripForm),
}

@staff_only
def edit(request,kind,object_id):
	"""
	Edit model
	"""
	
	(model,model_form) = _supported_model[kind]
	
	message = ""
	
	object = get_object_or_404(model,key_name = object_id)
	
	if request.method == 'POST':
		form = model_form(request.POST,instance=object)
		if form.is_valid():
			old_rev = entityToText(createEntity(object))
			new_object = form.save(commit = False)
			new_rev = entityToText(createEntity(new_object))
			
			changelog = Changelog(
				reference = object,
				commit_date = datetime.utcnow(),
#				committer=request.user,
				comment=form.cleaned_data['log_message'],
				old_rev = old_rev,
				new_rev = new_rev,
				model_kind=kind,
				)
			
			db.put([new_object,changelog])
			updateCachedObject(new_object)
			
			#TODO - Update cache
			
			message = "The form is successfully saved. <a href='%s'>View.</a> " % object.get_absolute_url()

	else:
		form = model_form(instance=object)

	return render_to_response( 
		request,
		'gogogo/db/edit.html'
		,{ "form" : form , 
		   "object" : object,
		   "message" : message,
		   "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
		   "view_object_link" : object.get_absolute_url(),
		   "action" : _reverse('gogogo.views.db.edit',args=[kind,object_id]) ,
		   })		

	
	
	
