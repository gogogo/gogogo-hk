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
from ragendja.dbutils import get_object_or_404
#from gogogo.views.db import reverse as db_reverse
from django.core.urlresolvers import reverse
from gogogo.models.loaders import RouteListLoader

import cgi
import logging

def search(request):
    """
    Route searching
    """	
    error = None
    agency = None
    if "agency" in request.GET:
        agency_id = request.GET['agency']
        agency = db.Key.from_path(Agency.kind(),agency_id)

    if "keyword" not in request.GET:
        return render_to_response( 
            request,
            'gogogo/route/search.html'
            ,{ 
                'page_title': _("Route searching"),
                'result' : [],
                'error' : _("Error! No keyword provided!")
               })
        
    keyword = request.GET['keyword']
    keyword = keyword.lower()

    route_list_loader = RouteListLoader()
    route_list_loader.load()
    
    route_list = route_list_loader.get_list()
    
    result = []
    
    agency_property = getattr(Route,"agency")

    for route in route_list:
        if agency:
            key = agency_property.get_value_for_datastore(route)
            if agency != key:
                continue

        if route.short_name.find(keyword) != -1:
            result.append(route)
            continue
            
        for name in route.long_name:
            if name.lower().find(keyword)!= -1:
                result.append(route)
                continue
            
    result = [createEntity(route) for route in result  ]
        
    return render_to_response( 
        request,
        'gogogo/route/search.html'
        ,{ 
            'page_title': _("Route searching"),
            'result' : result,
            'error' : error
           })		
	
