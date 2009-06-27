
from gogogo.models import *
from ragendja.auth.decorators import staff_only
from ragendja.dbutils import get_object_or_404
from django.forms import ModelForm
from ragendja.template import render_to_response

from django.core.urlresolvers import reverse as _reverse

def reverse(object):
	"""
	Return the link to the object
	"""
	
	if isinstance(object,Agency):
		ret = _reverse('gogogo.views.transit.agency',args=[object.key().name()] )
	elif isinstance(object,Route):
		ret = _reverse('gogogo.views.transit.route',args=[object.agency.key().name(),object.key().name()] )
	elif isinstance(object,Trip):
		ret = _reverse('gogogo.views.transit.trip',args=[object.route.agency.key().name(),
			object.route.key().name(),
			object.key().name()] )
	else:
		raise ValueError("gogogo.views.db.reverse() do not support %s" % object.kind() )	

	return ret

class AgencyForm(ModelForm):
	class Meta:
		model = Agency
		fields = ['name','phone','url','icon']

class RouteForm(ModelForm):
	class Meta:
		model = Route
		fields = ['agency','short_name','long_name','desc','type','url','color','text_color']

class TripForm(ModelForm):
	class Meta:
		model = Trip
		exclude = ["stop_list"]

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
	#object_entity = create_entity(object)
	
	if request.method == 'POST':
		form = model_form(request.POST,instance=object)
		if form.is_valid():
			form.save()
			message = "The form is successfully saved. <a href='%s'>View.</a> " % reverse(object)

	else:
		form = model_form(instance=object)

	return render_to_response( 
		request,
		'gogogo/db/edit.html'
		,{ "form" : form , 
		   "object" : object,
		   "message" : message,
		   "reverse" : reverse(object),
		   "action" : _reverse('gogogo.views.db.edit',args=[kind,object_id]) ,
		   })		

	
	
	
