# Create your views here.

from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader , RequestContext
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from models import *


def agency_list(request):
	"""
	List all agency
	"""
	query = Agency.all()
	text = ""
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
	
	t = loader.get_template('gogogo/agency/browse.html')
	c = RequestContext(
		request,
	{
        'page_title': agency['name'] ,
        'agency' : agency
    })
    		
	return HttpResponse(t.render(c))
	
	
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
	
	
