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
		agency_list.append(create_entity(row,request))
	
	t = loader.get_template('gogogo/agency/list.html')
	c = RequestContext(
		request,
	{
        'page_title': _("Agency List"),
        'agency_list' : agency_list
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
	
	
