import math

class LatLng:
	"""
	LatLng is a point in geographical coordinates with latitude and longitude.
	"""

	# Radius of earth
	R = 6371
	
	def __init__(self,lat=0,lng=0):
		assert (lat >= -90 and lat <= 90 and lng >= -180 and lng <= 180)
		self.lat = lat
		self.lng = lng
		self.data = None
		
	def distance(self,other):
		"""
			The distance between another point
			
			@return The distance in km
		
		Test to calculate the distance between (53 09 02N,001 50 40W),(52 12 17N,000 08 26E)
		http://www.movable-type.co.uk/scripts/latlong.html

		>>> a = LatLng(53.15055555555556 , -1.84444444444444)
		>>> b = LatLng(52.20472222222222, 0.14055555555556)
		
		>>> "%0.1f" % a.distance(b)
		'170.2'
		
		"""
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
		
	def bearing(self,other):
		"""
			Calculate the bearing to another point (in degree)
		>>> a = LatLng(53.15055555555556 , -1.84444444444444)
		>>> b = LatLng(52.20472222222222, 0.14055555555556)
				
		>>> "%0.2f" % LatLng.r2d(a.bearing(b))
		'127.37'
		
		#Testing data generated from Google Maps
		>>> c = LatLng(22.40866671626623,114.0500717256725)
		>>> d = LatLng(22.48258531104224,114.1215846968101)
		>>> "%0.2f" % LatLng.r2d(c.bearing(d))
		'41.79'
			
		"""
		if (self == other):
			return 0
		
		lat1 = self.lat * math.pi / 180
		
		lat2 = other.lat * math.pi / 180
		
		dLon = (other.lng - self.lng)  * math.pi / 180
		
		y = math.sin(dLon) * math.cos(lat2)
		
		x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
	
		return  math.atan2(y, x)
	
	def toString(self,precision):
		"""
		>>> LatLng(22.40866671626623,114.0500717256725).toString(2)
		'(22.41,114.05)'

		>>> LatLng(22.40866671626623,114.0500717256725).toString(6)		
		'(22.408667,114.050072)'
		"""		
		
		format = "(%%0.%df,%%0.%df)" %  (precision,precision)
		return format % (self.lat,self.lng)
	
	def __str__(self):		
		return "(%f,%f)" % (self.lat,self.lng)
	
	def __add__(self,other):
		return LatLng(self.lat + other.lat , self.lng + other.lng)
	
	def __div__(self,other):
		return LatLng(self.lat / other , self.lng / other)	
	
	def __eq__(self,other):
		return (self.lat == other.lat and self.lng == other.lng)

	def r2d(r):
		"""
			Convert from radians to degrees
			
			>>> "%0.2f" % LatLng.r2d(0.73739248129641422)
			'42.25'
		"""
		return (r * 180 / math.pi + 360)   % 360
		
	r2d = staticmethod(r2d)	
	
	def setData(self,data):
		"""
		Set user customized data
		"""
		self.data = data
		
	def getData(self):
		"""
		Get user customized data
		"""
		return self.data

if __name__ == "__main__":
	import doctest
	doctest.testmod(verbose=True)

 
