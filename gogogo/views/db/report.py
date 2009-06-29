"""
Invalid information report function
"""

from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader , RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import ModelForm
from django.forms import Widget
from django.forms.widgets import Input
from django.http import HttpResponseRedirect

from ragendja.auth.decorators import staff_only , login_required , google_login_required
from ragendja.template import render_to_response
from gogogo.models import *
#from gogogo.views.db import reverse as db_reverse
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from gogogo.models.cache import getCachedObjectOr404
from gogogo.models.utils import createEntity
from gogogo.views.widgets import ReferenceLinkField

class ReportForm(ModelForm):
	subject = forms.CharField(required=True)
	detail = forms.CharField(required=True,widget=forms.Textarea)
	#reference = ReferenceLinkField(required=False,widget = ReferenceLinkWidget())
	reference = ReferenceLinkField()
	
	class Meta:
		model = Report
		fields = ['reference','subject','detail']
		exclude = ('committer' , 'status' , )
	
_supported_model={}
for m in  [Agency,Route,Trip]:
	_supported_model[m.kind()] = m 	 

def list(request):
	"""
	List report
	"""
	kind = None
	
	limit = 10
	offset = 0

	if request.method == "GET":
		if "limit" in request.GET:
			limit = int(request.GET['limit'])
		if "offset" in request.GET:
			offset = int(request.GET['offset'])
			if offset < 0 :
				offset = 0
		if "kind" in request.GET:
			kind = request.GET['kind']
	
	if kind is not None:
		gql = db.GqlQuery("SELECT * from gogogo_report WHERE model_kind = :1 ORDER BY commit_date DESC ",kind)
	else:
		gql = db.GqlQuery("SELECT * from gogogo_report ORDER BY commit_date DESC ")		

	query = gql.fetch(limit,offset)
		
	result = []

	count = 0
	for row in query :
		count+=1
		entity = createEntity(row)
		entity['id'] = row.key().id()
		result.append(entity)
	
	prev_offset = offset - limit
	if prev_offset < 0 :
		prev_offset = 0
	
	return render_to_response( 
		request,
		'gogogo/db/report/list.html',
			{ "result" : result,
			  "offset" : offset + limit,
			  "prev_offset" : prev_offset,
			  "show_next" : count == limit,
			  "show_prev" : offset != 0,
			  "kind" : kind
		   })			

@google_login_required
def submit(request,kind,id):
	"""
	Submit a new report
	"""
	
	kind = "gogogo_" + kind
	if not kind in _supported_model:
		raise Http404
	model = _supported_model[kind]
	
	object = getCachedObjectOr404(model,key_name = id)
	
	report = Report(reference = object)
	message = ""
	
	if request.method == 'POST':
		form = ReportForm(request.POST,instance=report)
		if form.is_valid():
			form.cleaned_data['reference'] = object
			form.save()
			return HttpResponseRedirect(object.get_absolute_url())
		else:
			form.reference = object
	else:
		form = ReportForm(instance=report)
	
	return render_to_response( 
		request,
		'gogogo/db/report/submit.html',
		{ "form" : form , 
		"message" : message
		   })		
