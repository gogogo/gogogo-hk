import math

class LatLng:

	R = 6371
	
	def __init__(self,lat=0,lng=0):
		assert (lat >= -90 and lat <= 90 and lng >= -180 and lng <= 180)
		self.lat = lat
		self.lng = lng

	def distance(self,other):
		if (self == other):
			return 0
		lat1 = self.lat * math.pi / 180
		
		lat2 = other.lat * math.pi / 180
		
		delta = (other.lng - self.lng)  * math.pi / 180
		
		try:
			ret =  math.acos(math.sin(lat1)*math.sin(lat2) + 
					  math.cos(lat1)*math.cos(lat2) *
					  math.cos(delta))	* LatLng.R;
		except ValueError,v:
			print(self)
			print(other)
			raise v
		return ret
	
	def __str__(self):
		return "(%f,%f)" % (self.lat,self.lng)
	
	def __add__(self,other):
		return LatLng(self.lat + other.lat , self.lng + other.lng)
	
	def __div__(self,other):
		return LatLng(self.lat / other , self.lng / other)	
	
	def __eq__(self,other):
		return (self.lat == other.lat and self.lng == other.lng)

