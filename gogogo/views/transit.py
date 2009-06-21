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

def index(request):
	"""
	Show transit information
	"""

	query = Agency.all()
	
	agency_list = []
	for row in query:
		entity = create_entity(row,request)
		entity['key_name'] = row.key().name()
		agency_list.append(entity)

	return render_to_response( 
		request,
		'gogogo/transit/index.html'
		,{ 
			'page_title': _("Transit Information"),
		   "agency_list" : agency_list,
		   })		

def agency(request,agency_id):
	"""
	Browse the information of a transport agency
	"""

	try:
		key = db.Key.from_path(Agency.kind(),agency_id)
	
		record = db.get(key)
	except (db.BadArgumentError,db.BadValueError):
		raise Http404
	
	if record == None:
		raise Http404
		
	agency = create_entity(record,request)
	agency['key_name'] = record.key().name()
	
	gql = db.GqlQuery("SELECT * FROM gogogo_route where type = :1 and agency=:2",2,record)
	rail_list = []
	for row in gql:
		entity = create_entity(row,request)
		entity['key_name'] = row.key().name()
		rail_list.append(entity) 
	
	t = loader.get_template('gogogo/transit/agency.html')
	c = RequestContext(
		request,
	{
        'page_title': agency['name'] ,
        'agency' : agency,
        'rail_list' : rail_list
    })
    		
	return HttpResponse(t.render(c))

def route(request,agency_id,route_id):
	"""
	Browse the information of a route data
	"""

	try:
		key = db.Key.from_path(Route.kind(),route_id)
	
		record = db.get(key)
	except (db.BadArgumentError,db.BadValueError):
		raise Http404

	lang = MLStringProperty.get_current_lang(request)
	entity = {
		'key_name' : record.key().name(),
		'long_name' : MLStringProperty.trans(record.long_name,lang),
		'short_name' : record.short_name,
		
		# Reduce the no. of database access
		'agency' : agency_id
		#'agency' : record.agency.key().name()
	}
	
	return render_to_response( 
		request,
		'gogogo/transit/route.html'
		,{ 
			'page_title': _("Transit Information"),
		   "route" : entity,
		   })		
