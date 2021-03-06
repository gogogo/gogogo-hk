from LatLng import LatLng
import copy

class LatLngGroup:
	"""
		Hold a group of LatLng points
	"""
	
	def __init__ (self , pts = []):
		"""
		
		>>> str(LatLngGroup([(22.35,114.17),(22.37,114.15)]))
		'(22.350000,114.170000).(22.370000,114.150000)'
		"""
		self.data = None
		self.pts = []
		for p in pts:
			if isinstance(p,LatLng):
				self.pts.append(p)
			elif isinstance(p,tuple):
				self.pts.append((LatLng(*p)))
			else:
				raise ValueError
		self.dirty = True
		
		# The fixed center point
		self.fixedCentroid = None
	
	def get_centroid(self):	
		"""
		
		@return A LatLng object of centroid
		
		>>> str(LatLngGroup([LatLng(0,0) , LatLng(10,0),LatLng(0,10),LatLng(10,10)]).get_centroid())
		'(5.000000,5.000000)'

		>>> str(LatLngGroup([LatLng(22.252195,113.866299)]).get_centroid())
		'(22.252195,113.866299)'
		"""
		if self.dirty:
			self._calc()
		return self.centroid
		
	def get_gdi(self):
		"""
			Get Group Distance Index (average)
		"""
		if self.dirty:
			self._calc()
		return self.gdi
		
	def get_radius(self):
		if self.dirty:
			self._calc()
		return self.radius
	
	def append(self,pt):
		"""
		@type pt gogogo.geo.LatLng
		"""
		self.pts.append(pt)
		self.dirty = True
		
	def remove(self,pt):
		self.pts.remove(pt)
		self.dirty = True
	
	def toString(self,precision):
		pts_str = []
		
		for p in self.pts:
			pts_str.append(p.toString(precision))
		
		return ",".join(pts_str)
		
	def dup(self):
		"""
			Duplicate a copy of this group exclude the contained
			points. 
		"""
		object = copy.copy(self)
		object.pts = self.pts[:]
		object.dirty = True
		return object
	
	def __str__(self):
		pts_str = []
		
		for p in self.pts:
			pts_str.append(str(p))
		
		return ".".join(pts_str)
		
	def __len__(self):
		return len(self.pts)
		
	def _calc(self):
		"""
			Calculate centroid and group distance index
		"""
		
		self.centroid = LatLng()
		self.gdi = 0
		self.radius = 0
		
		n = len(self.pts)
		if n > 0:
			self.radius = 0
			
			if self.fixedCentroid:
				self.centroid = self.fixedCentroid
			else:
				lat = 0
				lng = 0
				for pt in self.pts:
					lat += pt.lat
					lng += pt.lng
					
				self.centroid = LatLng(lat / n , lng / n)
			
			for pt in self.pts:
				dist = self.centroid.distance(pt)
				self.gdi += dist
				if dist > self.radius :
					self.radius = dist
			
			self.gdi /= n

		self.dirty = False
		
	def set_fixed_centroid(self,center):
		"""
		Set a fixed centroid. A group with fixed centroid always use the assigned
		point as the centroid independent of the points contained.
		
		>>> l = LatLngGroup([LatLng(0,0) , LatLng(10,0),LatLng(0,10),LatLng(10,10)])
		>>> l.set_fixed_centroid(LatLng(7,7))
		>>> str(l.get_centroid())
		'(7.000000,7.000000)'

		"""
		self.fixedCentroid = center
		self.dirty = True
	
	def get_fixed_centroid(self):
		return self.fixedCentroid

	def set_data(self,data):
		"""
		Set user customized data
		"""
		self.data = data
		
	def get_data(self):
		"""
		Get user customized data
		"""
		return self.data

if __name__ == "__main__":
	import doctest
	doctest.testmod(verbose=True)
