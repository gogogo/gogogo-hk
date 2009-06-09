from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.ext import bulkload

import sys
import os

sys.path.insert(0 , os.path.abspath(os.path.dirname(__file__) + "/../common/appenginepatch"))
sys.path.insert(0 , os.path.abspath(os.path.dirname(__file__) + "/../"))
import main
import gogogo.models

def convert_key_name_to_key(model,key_name):
	ret = None
	if key_name:
		object = model.get_by_key_name(key_name)
		if object:
			ret = object.key()
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
                                ('phone', str),
                               ])


class StopLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_stop',
                               [
#                               ('agency', db.Key),
                               ('key_name',str),
                               ('code',str),	
                               ('name', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('desc', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('lat',str),
                               ('lng',str),
                               ('zone_id',str),
                               ('url',str),
                               ('location_type',int),
                               ('parent_station',lambda x: convert_key_name_to_key(gogogo.models.Stop,x) ),
                               ])                               

loaders = [AgencyLoader,StopLoader]

