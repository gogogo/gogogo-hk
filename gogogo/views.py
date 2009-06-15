# Create your views here.

from django.http import HttpResponse
from django.http import Http404
from django.template import Context, loader
from django.conf import settings

from models import *


def agency(request):
	"""
		Handle query of agency information
	"""
	q = Agency.all()
	results = q.fetch(10)
	text = ""
	for p in results:
		text += p.name
	return HttpResponse(text)
	
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
	
	
