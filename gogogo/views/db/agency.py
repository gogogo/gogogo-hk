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
#from gogogo.views.db import reverse as db_reverse
from django.core.urlresolvers import reverse

def list(request):
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

def browse(request,id):
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
def edit(request,id):
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
			message = "The form is successfully saved. <a href='%s'>View.</a> " % record.get_absolute_url()

	else:
		form = AgencyForm(instance=record)

	agency = create_entity(record,request)
	agency['key_name'] = record.key().name()
	
	return render_to_response( 
		request,
		'gogogo/db/edit.html'
		,{ "form" : form , 
		   "agency" : agency,
		   "message" : message,
		   "action" : reverse('gogogo.views.db.agency.edit',args=(id,)) ,
		   })		
	
