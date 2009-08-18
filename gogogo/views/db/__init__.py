
###################################################################
# Database frontend (for advanced data viewing and editing)
###################################################################

from gogogo.models import *
from ragendja.auth.decorators import staff_only
from ragendja.dbutils import get_object_or_404
from django import forms
from django.forms import ModelForm
from ragendja.template import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect

from django.core.urlresolvers import reverse as _reverse
from gogogo.models.utils import createEntity , entityToText
from gogogo.models.cache import updateCachedObject
from datetime import datetime
from gogogo.models import TitledStringListField , MLStringProperty
import logging

class AgencyForm(ModelForm):
	class Meta:
		model = Agency
		fields = ['name','phone','url','icon']
		
	name = TitledStringListField(required = True , fixed_fields = MLStringProperty.get_lang_list())
		
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

def add(request,kind):
	"""
	Add new entry to database
	"""
	
	(model,model_form) = _supported_model[kind]
	
	if request.method == 'POST':
		form = model_form(request.POST)
		if form.is_valid():
			instance = form.save()

			old_rev = None
			new_rev = entityToText(createEntity(instance))
			
			changelog = Changelog(
				reference = instance,
				commit_date = datetime.utcnow(),
#				committer=request.user,
				comment=form.cleaned_data['log_message'],
				old_rev = old_rev,
				new_rev = new_rev,
				model_kind=kind,
				type=1
				)

			changelog.save()
			
			return HttpResponseRedirect(instance.get_absolute_url())
	else:
		form = model_form()
		
	message = ""

	return render_to_response( 
		request,
		'gogogo/db/edit.html'
		,{ "form" : form , 
		   "kind" : kind,
		   "message" : message,
		   "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
		   "action" : _reverse('gogogo.views.db.add',args=[kind]) ,
		   })		


@staff_only
def edit(request,kind,object_id):
	"""
	Edit model
	"""
	
	(model,model_form) = _supported_model[kind]
	
	message = ""

	id = None
	key_name = None
	try:
		id = int(object_id)
	except ValueError:
		key_name = object_id
	
	object = get_object_or_404(model,key_name = key_name , id=id)
		
	
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

	view_object_link = None
	if object : 
		view_object_link = object.get_absolute_url()
		
	return render_to_response( 
		request,
		'gogogo/db/edit.html'
		,{ "form" : form , 
		   "object" : object,
		   "kind" : kind,
		   "message" : message,
		   "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
		   "view_object_link" : view_object_link,
		   "action" : _reverse('gogogo.views.db.edit',args=[kind,object_id]) ,
		   })		

	
	
	
