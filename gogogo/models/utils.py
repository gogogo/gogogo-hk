from google.appengine.api import memcache
from ragendja.dbutils import get_object_or_404
from google.appengine.ext import db
import logging
from gogogo.models import MLStringProperty

def createEntity(object):
	"""  Create an entity from model instance object which is 
	suitable for data import and export. 


	Opertions:
	
	- Convert all ReferenceProperty to the key_name/key

	"""
	entity = {}
	
	for prop in object.properties().values():
		datastore_value = prop.get_value_for_datastore(object)
		if not datastore_value == []:
			entity[prop.name] = datastore_value
			
			if isinstance(prop,db.ReferenceProperty):
				if datastore_value:
					entity[prop.name] = datastore_value.name()
			elif isinstance(prop,MLStringProperty):
				entity[prop.name] = u'|'.join(datastore_value)

	entity['key_name'] = object.key().name()
	entity['instance'] = object
	return entity

def entityToText(entity):
	
	bad_word = ['key_name' , 'instance']
	
	text = u"key_name : %s\n" % entity['key_name']
	
	fields = []
	for prop in entity:
		if prop not in bad_word:
			if isinstance(prop,list):
				fields.append(u"%s: %s" % (prop,u','.join(entity[prop])) )
			else:
				fields.append(u"%s: %s" % (prop,entity[prop]) )
			
	return text + u"\n".join(fields)
