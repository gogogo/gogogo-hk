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
from gogogo.models.cache import getCachedObjectOr404 , getCachedEntityOr404

_default_cache_time = 3600

def browse(request,id):
	"""
	Browse the information of a shape
	"""
	entity = getCachedEntityOr404(Shape,key_name = id)
	
	t = loader.get_template('gogogo/db/shape/browse.html')
	c = RequestContext(
		request,
	{
        'page_title': entity['key_name'] ,
        'shape' : entity
    })
    		
	return HttpResponse(t.render(c))	
	
		
	
	
