from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader , RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import ModelForm

from ragendja.auth.decorators import staff_only
from ragendja.template import render_to_response
from gogogo.models import *
from ragendja.dbutils import get_object_or_404
#from gogogo.views.db import reverse as db_reverse
from django.core.urlresolvers import reverse

import cgi

def search(request):
	"""
	Route searching
	"""	
	
	agency = None
	try:
		agency_id = request.GET['agency']
		key = db.Key.from_path(Agency.kind(),agency_id)
		agency = db.get(key)
	except:
		pass
	
	route_search = None
	try:
		route_search = request.GET['route']
	except:
		pass

	if agency:
		gql = db.GqlQuery("SELECT * FROM gogogo_route where short_name = :1 and agency=:2",route_search,agency)
	else:
		gql = db.GqlQuery("SELECT * FROM gogogo_route where short_name = :1",route_search)

	result = []
	
	for row in gql:
		entity = create_entity(row,request)
		entity['id'] = row.key().id_or_name()
		entity['agency'] = row.agency.key().name()
		result.append(entity)

	return render_to_response( 
		request,
		'gogogo/route/search.html'
		,{ 
			'page_title': _("Route searching"),
			'result' : result
		   })		
	
class Form(ModelForm):
	class Meta:
		model = Route
		fields = ['short_name','long_name','desc']
		
@staff_only
def edit(request,id):
	"""
	Edit route information (staff only)
	"""
	
	record = get_object_or_404(Route,key_name=id)	

	message=""

	if request.method == 'POST':
		form = Form(request.POST,instance=record)
		if form.is_valid():
			form.save()
			message = "The form is successfully saved. <a href='%s'>View.</a> " % record.get_absolute_url()

	else:
		form = Form(instance=record)

	agency = create_entity(record,request)
	agency['id'] = record.key().id_or_name()
	
	return render_to_response( 
		request,
		'gogogo/db/edit.html'
		,{ "form" : form , 
		   "agency" : agency,
		   "message" : message,
		   "action" : reverse('gogogo.views.db.route.edit',args=[id,]) ,
		   })		

	
