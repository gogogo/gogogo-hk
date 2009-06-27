from google.appengine.api import memcache
from ragendja.dbutils import get_object_or_404
from google.appengine.ext import db
import logging

def getCachedObjectOr404(model,key=None,key_name=None):
	"""
	Get a object from cache. If it is not existed in the cache, 
	it will query from database directly and save it in cache.
	
	If the object is not existed in the cache and database , it 
	will raise Http404 exception
	"""

	if key:
		key_object = db.Key(key)
	elif key_name:
		key_object = db.Key.from_path(model.kind(),key_name)
	else:
		raise ValueError("Not enough argument")
		
	cache_key = "gogogo__key__%s" % str(key_object) 
	print cache_key
	object = memcache.get(cache_key)
	
	if object == None:
		object = get_object_or_404(model, key=key,key_name=key_name)
		if not memcache.add(cache_key, object, 10):
			logging.error("Memcache set %s failed." % cache_key)

	return object
