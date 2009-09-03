from google.appengine.ext import db
from google.appengine.api import datastore_types

from django.utils import simplejson
from gogogo.models import Changelog

from datetime import datetime
import time
import codecs
from StringIO import StringIO
import logging

def createChangelog(old_object , new_object,comment):
    """
    Create a Changelog instance
    """
    old_rev = None
    new_rev = None
    
    if old_object == None: # Add a new record
        type = 1
        kind = new_object.kind()
        instance = new_object
        
        entity = serialize(new_object)
        
        content = StringIO()
        simplejson.dump(entity,content,ensure_ascii=False,indent =1)
        
        new_rev = content.getvalue()
    elif old_object != None and new_object != None:
        type = 0
        kind = new_object.kind()
        instance = new_object
        
        old_entity = serialize(old_object)
        new_entity = serialize(new_object)
    
        content = StringIO()
        
        simplejson.dump(old_entity,content,ensure_ascii=False,indent =1)
        old_rev = content.getvalue()
        
        content = StringIO()
        
        simplejson.dump(new_entity,content,ensure_ascii=False,indent =1)
        new_rev = content.getvalue()
    
    changelog = Changelog(
        reference = instance,
        commit_date = datetime.utcnow(),
#				committer=request.user,
        comment=comment,
        old_rev = old_rev,
        new_rev = new_rev,
        model_kind=kind,
        type=type
        )

    return changelog    
    
    

#######################################################################
#
# The code below is based on the source code from gaescripts 
# project.
#
#######################################################################

def resolve_key(key_data,reference_class):
    """
    Resolve the key and create key instance
    """
    
    if isinstance(key_data, list): # If it is a path
        return db.Key.from_path(*key_data)
    elif isinstance(key_data, basestring):
        try:
            return db.Key(key_data) #Encoded data
        except datastore_types.datastore_errors.BadKeyError, e:
            if reference_class == db.Model:
                logging.error("Invalid Reference")
                return key_data
            else:
                return db.Key.from_path(reference_class.kind(),key_data)   

def encode_key(key,reference_class,field):
    """
    Encode a key for JSON output
    """
    if reference_class != db.Model:
        return key_name
    else:
        if key.id() == None:
            return str(key)
        else:
            key = db.Key.from_path( key.kind() , key_name )
            return str(key)

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

    return entity

def deserialize(model_class,entity):
    """
    Create a model instance from json
    """
    from google.appengine.ext import db
    from ragendja.dbutils import KeyListProperty
    from google.appengine.api.users import User       
    
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
