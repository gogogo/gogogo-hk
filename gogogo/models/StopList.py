from gogogo.models import *

class StopList:
	"""
	Process Trip.stop_list to extract stop information.
	"""

	def __init__(self,trip):		
		# The first stop
		self.first = None
		try:
			self.first = db.get(trip.stop_list[0])
			self.last = db.get(trip.stop_list[len(trip.stop_list)-1])
		except IndexError:
			self.last = self.first

		self.data = []

		for key in trip.stop_list:
			stop = db.get(key)
			self.data.append( { 
				"key_name" : key.name(),
				"object"	: stop
			})

	def createTREntity(self,request):
		"""
		Create entity with translated entity
		"""
		
		lang = MLStringProperty.get_current_lang(request)
		
		data = []
		for stop in self.data:
			entity = {
				'key_name' : stop['key_name'],
				'name' : MLStringProperty.trans(stop['object'].name,lang  )
			}
			data.append(entity)
		
		ret = {
			'first' : create_entity(self.first,lang),
			'last' : create_entity(self.last,lang),
			'data' : data
		}
		
		return ret
