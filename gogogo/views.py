# Create your views here.

from django.http import HttpResponse
from django.template import Context, loader
from models import *

def agency(request):
	q = Agency.all()
	results = q.fetch(10)
	text = ""
	for p in results:
		text += p.name
	return HttpResponse(text)
	
	
