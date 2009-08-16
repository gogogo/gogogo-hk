from google.appengine.api import memcache
from ragendja.dbutils import get_object_or_404
from google.appengine.ext import db
import logging
from MLStringProperty import MLStringProperty
from ragendja.dbutils import KeyListProperty

def createEntity(object):
	"""  Create an entity from model instance object which is 
	suitable for data import and export. 

	Opertions:
	- Convert all ReferenceProperty to the key_name/key
	- set 'key_name' attribute
	- set 'instance' attribute , the reference to the model instance
	
	@return A dict object contains the entity of the model instance. The fields are not translated , use trEntity to translate to user's locale

	"""
	entity = {}
	
	for prop in object.properties().values():
		datastore_value = prop.get_value_for_datastore(object)
		if not datastore_value == []:
			entity[prop.name] = datastore_value
			
			if isinstance(prop,db.ReferenceProperty):
				if datastore_value:
					entity[prop.name] = datastore_value.id_or_name()
			elif isinstance(prop,MLStringProperty):
				entity[prop.name] = u'|'.join(datastore_value)
			elif isinstance(prop,KeyListProperty):
				logging.info("KeyListProperty is not supported")
				del entity[prop.name]
			
	entity['key_name'] = object.key().id_or_name() #TODO Deprecate
	entity['id'] = object.key().id_or_name()
	entity['instance'] = object
	return entity

def trEntity(entity,request):
	"""
	Translate an entity 
	"""
	ret = {}
	ret.update(entity)
	
	lang = MLStringProperty.get_current_lang(request)
	
	for prop in entity['instance'].properties().values():
		datastore_value = prop.get_value_for_datastore(entity['instance'])
		if not datastore_value == []:
			ret[prop.name] = datastore_value
			
			if request and isinstance(prop,MLStringProperty):
				
				ret[prop.name] = MLStringProperty.trans(datastore_value,lang)

	return ret

def entityToText(entity):
	"""
	Convert entity to text object. (For debugging and changelog generation)
	"""
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
