from google.appengine.api import memcache
from ragendja.dbutils import get_object_or_404
from google.appengine.ext import db
import logging


def createEntity(object):
	"""  Create an entity from model instance object which is 
	suitable for data import and export. 

	"""
	entity = {}
	
	for prop in object.properties().values():
		datastore_value = prop.get_value_for_datastore(object)
		if not datastore_value == []:
			entity[prop.name] = datastore_value
			
			if isinstance(prop,db.ReferenceProperty):
				entity[prop.name] = prop.key().name()

	entity['key_name'] = object.key().name()
	entity['instance'] = object
	return entity

def entityToText(entity):
	
	bad_word = ['key_name' , 'instance']
	
	text = u"key_name : %s\n" % entity['key_name']
	
	fields = []
	for prop in entity:
		if prop not in bad_word:
			fields.append(u"%s : %s" % (prop,entity[prop]) )
			
	return text + u"\n".join(fields)
