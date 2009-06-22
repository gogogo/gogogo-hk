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

import re

def find_stop_id(request):
	"""
	Find stop id
	"""
	
	result_list = []
	stop_list = []
	
	if request.method == "POST":
		
		# Agency field is not available for STOP yet
		#key = db.Key.from_path(Agency.kind(),request.POST['agency'])
		#agency = db.get(key)
		
		#text = unicode(request.POST['text'])
		text = request.POST['text']
		
		stop_list = text.split(u'\n')
		for (i,stop) in enumerate(stop_list):
			stop_list[i] = stop_list[i].strip('\n')
			stop_list[i] = stop_list[i].strip('\r')
			stop_list[i] = stop_list[i].strip(' ')
			result_list.append([])
		
		gql = db.GqlQuery("SELECT * FROM gogogo_stop where location_type = :1",1)
		
		for row in gql:
			for (i,stop) in enumerate(stop_list):
				for name in row.name:
					if len(stop) > 0 and (re.search(stop,name) != None):
						result_list[i].append(row.key().name())
						break
						
		for (i,result) in enumerate(result_list):
			result_list[i]	 = ','.join(result_list[i])
	
	lang = MLStringProperty.get_current_lang(request)
	
	query = Agency.all()
	agency_list = []
	for agency in query:
		agency_list.append( (agency.key().name() , MLStringProperty.trans(agency.name,lang) ))
		
	return render_to_response( 
		request,
		'gogogo/devtools/FindStopID.html'
		,{ 'agency_list' : agency_list,
			'result_list' : result_list,
			'output' : '\n'.join(result_list),
			'stop_list' :stop_list,
			'input': '\n'.join(stop_list),
		   })		
	
	
