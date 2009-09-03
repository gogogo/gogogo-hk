from google.appengine.api import memcache
from ragendja.dbutils import get_object_or_404
from google.appengine.ext import db
import logging
from MLStringProperty import MLStringProperty
from ragendja.dbutils import KeyListProperty
from gogogo.geo import LatLng

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

	Operations:
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
	if object.is_saved():
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

def latlngFromGeoPt(pt):
    """
    Construct LatLng object db.GeoPt instance
    """
    return LatLng(pt.lat,pt.lon)

def copyModel(object, **kwargs):
    """
    Copy a model instance
    
    @param kwargs Argument passed to the model constructor funtion for new copied model
    """
    model_class = db._kind_map[object.kind()]
    
    entity = {}
    
    for prop in object.properties().values():
        datastore_value = prop.get_value_for_datastore(object)
        entity[prop.name] = datastore_value
        
    entity.update(kwargs)
        
    return model_class(**entity)
 
#
#  serialize & deserialize are based on the code from 
#  gaescript project
#
        
def serialize(object):
    """ 
    Serialize a model instance to basic Python object

    Operations:
    - Convert all ReferenceProperty to the key_name/key
    """
    entity = {}
    
    for prop in object.properties().values():
        datastore_value = prop.get_value_for_datastore(object)
        if datastore_value == None:
            continue
        
        entity[prop.name] = datastore_value
        
        if isinstance(prop,db.ReferenceProperty):
            entity[prop.name] = encode_key(datastore_value,prop.reference_class,prop.name)
        elif isinstance(prop,db.GeoPtProperty):
            entity[prop.name] = (datastore_value.lat,datastore_value.lon)
        elif isinstance(prop,db.UserProperty):
            entity[prop.name] = datastore_value.email()
        elif isinstance(prop,db.DateTimeProperty):
            entity[prop.name] = time.mktime(datastore_value.timetuple())  

    if object.key().id() != None:
        entity['id'] = object.key().id()
    else:
        entity['key_name'] = object.key().name()


    return entity

def deserialize(model_class,entity):
    """
    Create a model instance from json
    """
    from google.appengine.ext import db
    from ragendja.dbutils import KeyListProperty
    from google.appengine.api.users import User    
    
    # GAE can not restore numeric ID entity
    if "id" in entity:
        id = entity ["id"]
        del entity["id"]
        entity["key_name"] = id_prefix + str(id)
        print "Warning. The entity with ID %d will be renamed to %s. Old record will be removed." % (id,entity["key_name"])
    
    for prop in model_class.properties().values():
        if not prop.name in entity:
            continue

        if isinstance(prop,db.GeoPtProperty):
            field = u",".join([str(v) for v in entity[prop.name]])
            entity[prop.name] = field
            
        elif isinstance(prop,db.ReferenceProperty):
            
            entity[prop.name] = resolve_key(entity[prop.name] , prop.reference_class)

        elif isinstance(prop,KeyListProperty):
            items = []
            for key in entity[prop.name]:
                items.append(resolve_key(key,prop.reference_class))
                
            entity[prop.name] = items
        elif isinstance(prop,db.UserProperty):
            entity[prop.name] = User(email = entity[prop.name])
        elif isinstance(prop,db.DateTimeProperty):
            entity[prop.name] = datetime.datetime.fromtimestamp(entity[prop.name])
        
        if prop.name in entity and entity[prop.name] == None:
            del entity[prop.name]
    
    ret = {}        
    for key in entity: #Convert unicode key to str key
        ret[str(key)] = entity[key]

    object = model_class(**ret)
        
    return object        
            

