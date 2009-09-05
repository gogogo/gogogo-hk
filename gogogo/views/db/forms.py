from gogogo.models import *
from ragendja.auth.decorators import staff_only
from ragendja.dbutils import get_object_or_404
from django import forms
from django.forms import ModelForm
from ragendja.template import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse as _reverse
from gogogo.models.utils import createEntity , entityToText
from gogogo.models.cache import updateCachedObject
from datetime import datetime
from gogogo.models import TitledStringListField
from gogogo.models.MLStringProperty import MLStringProperty , to_key_name
from gogogo.models.utils import id_or_name
from gogogo.views.widgets import LatLngInputWidget
from gogogo.models.forms import AgencyForm , StopForm , TripForm , RouteForm
from gogogo.models.changelog import createChangelog

import logging

_supported_model = {
	'route' : (Route,RouteForm),
	'agency' : (Agency,AgencyForm),
	'trip' : (Trip,TripForm),
	'stop': (Stop,StopForm),
}

def next_key_name(model_class,key_name):
    """
    Get the next available key
    """
    if key_name == None:
        return key_name # Use numeric key
    
    entity = model_class.get(db.Key.from_path(model_class.kind() , key_name))

    if not entity:
        return key_name
    else:
        count = 0
        while True:
            count += 1
            new_key_name = key_name + "-" + str(count)
            entity = model_class.get(db.Key.from_path(model_class.kind() , new_key_name))
            if not entity:
                return new_key_name 

def _getModelInfo(kind):
    return _supported_model[kind]

def _createModel(kind,parent = None,form = None):
    value = id_or_name(parent)
    key_name = None
    if kind == "route":
        agency = None
        if form:
            agency = form.cleaned_data["agency"]
            key_name = next_key_name(Route,Route.gen_key_name(
                agency = agency,
                short_name = form.cleaned_data["short_name"],
                long_name = form.cleaned_data["long_name"],
                ))
                
        if parent:
            agency = db.Key.from_path(Agency.kind() , value)
            
        return Route(key_name = key_name,agency = agency)
    elif kind == "agency":
        if form:
            key_name = next_key_name(Agency,Agency.gen_key_name(name = form.cleaned_data["name"]))
            
        return Agency(key_name = key_name)
    elif kind == "trip":
        route = None
        if form:
            route = form.cleaned_data["route"]
            key_name = next_key_name(Trip, 
                route.key().name() + 
                "_to_" + 
                MLStringProperty.to_key_name(form.cleaned_data["headsign"]) )
        
        if parent:
            route = db.Key.from_path(Route.kind() , value)
        
        return Trip(route = route , key_name = key_name)
    elif kind == "stop":
        return Stop()
        
    raise ValueError

@staff_only
def add(request,kind):
    """
    Add new entry to database
    """

    (model,model_form) = _getModelInfo(kind)

    if request.method == 'POST':
        form = model_form(request.POST)
        
        if form.is_valid():
            instance = _createModel(kind,form = form)
            form = model_form(request.POST,instance = instance)

            instance = form.save(commit=False)		
            
            instance.save()

            #old_rev = None
            #new_rev = entityToText(createEntity(instance))
            changelog = createChangelog(None,instance,form.cleaned_data['log_message'])
            #changelog = Changelog(
                #reference = instance,
                #commit_date = datetime.utcnow(),
    ##				committer=request.user,
                #comment=form.cleaned_data['log_message'],
                #old_rev = old_rev,
                #new_rev = new_rev,
                #model_kind=kind,
                #type=1
                #)

            changelog.save()
            
            return HttpResponseRedirect(instance.get_absolute_url())
    elif request.method == 'GET':
        parent = None
        if "parent" in request.GET:
            parent = request.GET['parent']
        instance = _createModel(kind,parent)
        form = model_form(instance=instance)
        
    else:
        form = model_form()
        
    message = ""

    return render_to_response( 
        request,
        'gogogo/db/edit.html'
        ,{ "form" : form , 
           "kind" : kind,
           "message" : message,
           "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
           "action" : _reverse('gogogo.views.db.add',args=[kind]) ,
           })		


@staff_only
def edit(request,kind,object_id):
    """
    Edit model
    """

    (model,model_form) = _getModelInfo(kind)

    message = ""

    id = None
    key_name = None
    try:
        id = int(object_id)
    except ValueError:
        key_name = object_id

    object = get_object_or_404(model,key_name = key_name , id=id)

    if request.method == 'POST':
        form = model_form(request.POST,instance=object)
        if form.is_valid():
            
            #Old object was changed by the from, so it need to get a new copy
            object = get_object_or_404(model,key_name = key_name , id=id)
            new_object = form.save(commit = False)
            
            changelog = createChangelog(object,new_object,form.cleaned_data['log_message'])
            if changelog:                
            
                db.put([new_object,changelog])
                updateCachedObject(new_object)
                #TODO - Update loader cache
                
                message = _("The form is successfully saved. <a href='%s'>View.</a> ") % object.get_absolute_url()
            else:
                message = _("Nothing changed. The form will not be saved")

    else:
        form = model_form(instance=object)

    view_object_link = None
    if object : 
        view_object_link = object.get_absolute_url()
        
    return render_to_response( 
        request,
        'gogogo/db/edit.html'
        ,{ "form" : form , 
           "object" : object,
           "kind" : kind,
           "message" : message,
           "history_link" : _reverse('gogogo.views.db.changelog.list') + "?kind=%s" % kind,
           "view_object_link" : view_object_link,
           "action" : _reverse('gogogo.views.db.edit',args=[kind,object_id]) ,
           })		
