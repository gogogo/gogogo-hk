from gogogo.models import *

class StopList:
	"""
	Process Trip.stop_list to extract stop information.
	
	#TODO - Depcreate
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
				"id" : key.id_or_name(),
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
				'id' : stop['id'],
				'name' : MLStringProperty.trans(stop['object'].name,lang  )
			}
			data.append(entity)
		
		ret = {
			'first' : create_entity(self.first,request),
			'last' : create_entity(self.last,request),
			'data' : data
		}
		
		return ret
