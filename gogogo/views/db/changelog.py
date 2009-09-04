from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader , RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms import ModelForm

from django.utils import simplejson
from ragendja.auth.decorators import staff_only
from ragendja.template import render_to_response
from django.core.urlresolvers import reverse
from ragendja.dbutils import get_object_or_404
from gogogo.models import *

from gogogo.models.cache import getCachedEntityOr404
from gogogo.models.utils import createEntity

def list(request):
	"""
	List changelog
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
		gql = db.GqlQuery("SELECT * from gogogo_changelog WHERE model_kind = :1 ORDER BY commit_date DESC ",kind)
	else:
		gql = db.GqlQuery("SELECT * from gogogo_changelog ORDER BY commit_date DESC ")		

	query = gql.fetch(limit,offset)
		
	result = []

	count = 0
	for row in query :
		count+=1
		entity = createEntity(row)
		#entity['id'] = row.key().id_or_name()
		entity['type'] = Changelog.get_type_name(entity['type'])
		entity['entry_name'] = unicode(row.reference)
		result.append(entity)
	
	prev_offset = offset - limit
	if prev_offset < 0 :
		prev_offset = 0
	
	return render_to_response( 
		request,
		'gogogo/db/changelog/list.html',
			{ "result" : result,
			  "offset" : offset + limit,
			  "prev_offset" : prev_offset,
			  "show_next" : count == limit,
			  "show_prev" : offset != 0,
			  "kind" : kind
		   })		
	

def browse(request,id):
    """
    Browse a changelog
    """	

    entity = getCachedEntityOr404(Changelog,id_or_name = id)
    #entity['id'] = int(id)
    
    d = simplejson.loads(entity["changes"])
    
    entity["old_rev"] = d[0]["old"]
    entity["new_rev"] = d[0]["new"]

    return render_to_response( 
        request,
        'gogogo/db/changelog/browse.html',
            { "changelog" : entity,
            "reference_link" : entity['instance'].reference.get_absolute_url()
           })		
