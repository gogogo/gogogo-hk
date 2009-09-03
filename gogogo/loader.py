from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.ext import bulkload

import sys
import os

sys.path.insert(0 , os.path.abspath(os.path.dirname(__file__) + "/../common/appenginepatch"))
sys.path.insert(0 , os.path.abspath(os.path.dirname(__file__) + "/../"))
import main
import gogogo.models
import logging
from gogogo.models import *

def convert_key_name_to_key(model,key_name):
    if key_name == None or key_name == "":
        return None
    return db.Key.from_path(model.kind(),key_name)    

def convert_key_name_list_to_key_list(model,value):
    input = unicode(value,'utf-8').split(u',')
    ret = []
    for key_name in input:
        if len(key_name) > 0:
            ret.append(convert_key_name_to_key(model,key_name))
    return ret

def convert_to_list(value,sep,type):
	ret = value.split(sep)
	for i in range(0,len(ret)):
		try:
			ret[i] = type(ret[i])
		except ValueError:
			ret[i] = 0
	return ret

class AgencyLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_agency',
                               [
                                ('key_name',str),
                                ('name', lambda x: unicode(x,'utf-8').split(u'|') ),
                                ('url', str),
        						('timezone',str),                                
        						('lang',str),
                                ('phone', lambda x: unicode(x,'utf-8')),
                                ('icon',str)
                               ])


class StopLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_stop',
                               [
                               ('key_name',str),
                               ('agency',lambda x: convert_key_name_to_key(Agency,x) ),
                               ('code',str),	
                               ('name', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('desc', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('address', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('lat',str),
                               ('lng',str),
                               ('zone_id',str),
                               ('url',str),
                               ('location_type',int),
                               ('parent_station',lambda x: convert_key_name_to_key(Stop,x) ),
                               ])                               

class RouteLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_route',
                               [
                               ('key_name',str),
                               ('agency',lambda x: convert_key_name_to_key(gogogo.models.Agency,x)),	
                               ('short_name', lambda x: unicode(x,'utf-8') ),
                               ('long_name', lambda x: unicode(x,'utf-8').split(u'|') ),
                               #('desc', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('desc', lambda x: unicode(x,'utf-8')),
                               ('type',int),
                               ('url',str),
                               ('color',str),
                               ('text_color',str),
                               ])

class ShapeLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_shape',
                               [
                               ('key_name',str),
                               ('color',str),
                               ('type',int),
                               ('points' , lambda x: convert_to_list(x,u',',float)  ),
                               ])

class TripLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_trip',
                               [

                               ('route',lambda x: convert_key_name_to_key(gogogo.models.Route,x)),	
                               ('service',lambda x: convert_key_name_to_key(gogogo.models.Calendar,x)),	
                               ('key_name',str),
                               ('headsign', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('short_name', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('direction',int),
                               ('block',str),
                               ('shape',lambda x: convert_key_name_to_key(gogogo.models.Shape,x)),	
                               ('stop_list',lambda x: convert_key_name_list_to_key_list(gogogo.models.Stop,x)),
                               ('arrival_time_list' , lambda x: convert_to_list(x,u',',int) ),
                               ])


loaders = [AgencyLoader,StopLoader,RouteLoader,ShapeLoader,TripLoader]

