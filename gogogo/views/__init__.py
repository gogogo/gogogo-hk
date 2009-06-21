# Create your views here.

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

def transit(request):
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
		'gogogo/transit/transit.html'
		,{ 
			'page_title': _("Transit Information"),
		   "agency_list" : agency_list,
		   })		

def transit_browse(request,agency_id):
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
		rail_list.append(create_entity(row,request)) 
	
	t = loader.get_template('gogogo/transit/browse_agency.html')
	c = RequestContext(
		request,
	{
        'page_title': agency['name'] ,
        'agency' : agency,
        'rail_list' : rail_list
    })
    		
	return HttpResponse(t.render(c))

def agency_list(request):
	"""
	List all agency
	"""
	query = Agency.all()
	
	agency_list = []
	for row in query:
		entity = create_entity(row,request)
		entity['key_name'] = row.key().name()
		agency_list.append(entity)
	
	t = loader.get_template('gogogo/agency/list.html')
	c = RequestContext(
		request,
	{
        'page_title': _("Agency List"),
        'agency_list' : agency_list
    })
    		
	return HttpResponse(t.render(c))

def agency_browse(request,id):
	"""
	Browse the information of an agency
	"""
	try:
		key = db.Key.from_path(Agency.kind(),id)
	
		record = db.get(key)
	except (db.BadArgumentError,db.BadValueError):
		raise Http404
	
	if record == None:
		raise Http404
		
	agency = create_entity(record,request)
	agency['key_name'] = record.key().name()
	t = loader.get_template('gogogo/agency/browse.html')
	c = RequestContext(
		request,
	{
        'page_title': agency['name'] ,
        'agency' : agency
    })
    		
	return HttpResponse(t.render(c))

class AgencyForm(ModelForm):
	class Meta:
		model = Agency
		fields = ['name','phone','url','icon']

@staff_only
def agency_edit(request,id):
	"""
	Edit agency information (staff only)
	"""

	try:
		key = db.Key.from_path(Agency.kind(),id)
	
		record = db.get(key)
	except (db.BadArgumentError,db.BadValueError):
		raise Http404
	
	if record == None:
		raise Http404
	
	message = ""
	
	if request.method == 'POST':
		form = AgencyForm(request.POST,instance=record)
		if form.is_valid():
			form.save()
			message = "The form is successfully saved"

	else:
		form = AgencyForm(instance=record)

	agency = create_entity(record,request)
	agency['key_name'] = record.key().name()
	
	return render_to_response( 
		request,
		'gogogo/agency/edit.html'
		,{ "form" : form , 
		   "agency" : agency,
		   "message" : message
		   })		
	
def devtools(request,file):
	"""
		Handle the request to access devtools
	"""
		
	tools = ["MassAddressQuery.html" , "StopMaps.html"]
	
	if file not in tools:
		raise Http404
		
	t = loader.get_template("gogogo/devtools/" + file)
	c = Context({
        'GOOGLE_MAPS_KEY': settings.GOOGLE_MAPS_KEY,
	})
	return HttpResponse(t.render(c))
	
	
