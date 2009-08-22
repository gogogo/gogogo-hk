from google.appengine.api import memcache
from ragendja.dbutils import get_object_or_404
from google.appengine.ext import db
import logging
from MLStringProperty import MLStringProperty
from ragendja.dbutils import KeyListProperty

def id_or_name(id):
	"""
	Convert an ID used in javascript to id or key name in app engine
	"""
	if id == None:
		return None
	try:
		ret = int(id)
	except ValueError:
		ret = id
		
	return ret

def createEntity(object):
	"""  Create an entity from model instance object which is 
	suitable for data import and export. 

	Opertions:
	- Convert all ReferenceProperty to the key_name/key
	- set 'id' attribute (= id_or_name()
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
			
	#entity['key_name'] = object.key().id_or_name()
	
	# The client side do not know the different between id and key_name, they just 
	# "id" as the unique identifier of an entry
	entity['id'] = object.key().id_or_name()
	entity['instance'] = object
	return entity

def trEntity(entity,request):
	"""
	Translate an entity 
	"""
	if entity == None:
		return None
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
	banned = ['id' , 'key_name' , 'instance']
	
	text = u"id : %s\n" % entity['id']
	
	fields = []
	for prop in entity:
		if prop not in banned:
			if isinstance(prop,list):
				fields.append(u"%s: %s" % (prop,u','.join(entity[prop])) )
			else:
				fields.append(u"%s: %s" % (prop,entity[prop]) )
			
	return text + u"\n".join(fields)
