from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.ext import bulkload

import sys
import os

sys.path.insert(0 , os.path.abspath(os.path.dirname(__file__) + "/../common/appenginepatch"))
sys.path.insert(0 , os.path.abspath(os.path.dirname(__file__) + "/../"))
import main
import gogogo.models

class AgencyLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_agency',
                               [
                                ('aid',str),
                                ('name', lambda x: unicode(x,'utf-8').split(u'|') ),
                                ('url', str),
        						('timzone',str),                                
                                ('phone', str),
                               ])


class StopLoader(bulkloader.Loader):
	def __init__(self):
		bulkloader.Loader.__init__(self, 'gogogo_stop',
                               [
                               ('agency', gogogo.models.Agency.get_key),
                               ('sid',str),
                               ('code',str),	
                               ('name', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('desc', lambda x: unicode(x,'utf-8').split(u'|') ),
                               ('lat',str),
                               ('lng',str),
                               ('url',str),
                               ('location_type',int),
                               ('parent_station',gogogo.models.Stop.get_key),
                               ('inaccuray',bool),
                               ])

loaders = [AgencyLoader,StopLoader]

