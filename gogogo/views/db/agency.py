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
from gogogo.models.cache import getCachedEntityOr404
from google.appengine.api import memcache

# Shorter cache time for db object
_default_cache_time = 300

def list(request):
    """
    List all agency
    """
    
    lang = MLStringProperty.get_current_lang(request)
    cache_key = "gogogo_db_agency_list_%d" % lang
    cache = memcache.get(cache_key)

    if cache == None:
        query = Agency.all(keys_only=True)
	
        result = []
        for key in query:
            entity = getCachedEntityOr404(Agency,key = key)
            result.append(trEntity(entity,request))

        cache = {}
        cache['result'] = result
        memcache.add(cache_key, cache, _default_cache_time)
        
    agency_list = cache['result']
           
    t = loader.get_template('gogogo/db/agency/list.html')
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

    agency = getCachedEntityOr404(Agency,id_or_name=id)

    t = loader.get_template('gogogo/db/agency/browse.html')
    c = RequestContext(
        request,
    {
        'page_title': agency['name'] ,
        'agency' : agency
    })
            
    return HttpResponse(t.render(c))

