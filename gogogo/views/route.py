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
		entity['key_name'] = row.key().name()
		entity['agency'] = row.agency.key().name()
		result.append(entity)

	return render_to_response( 
		request,
		'gogogo/route/search.html'
		,{ 
			'page_title': _("Route searching"),
			'result' : result
		   })		
	
