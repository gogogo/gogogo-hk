from LatLng import LatLng
from LatLngGroup import LatLngGroup

class ConvexHull:
	"""
		Compute the convex hull from a LatLngGroup using Graham Scan
	"""
	
	def __init__ (self,group):
		self.group = group
		self.polygon = []
		
		# Start point of Graham Scan
		self.start = None 
		
		self._grahamScan()
		
	def ccw(p1,p2,p3):
		"""
		
		@return < 0 : Right , 0 : collinear , > 0 : Left 

		>>> ConvexHull.ccw(LatLng(0,0) , LatLng(5,5),LatLng(10,10))
		0
		>>> ConvexHull.ccw(LatLng(0,0) , LatLng(5,5),LatLng(20,10)) > 0
		True
		>>> ConvexHull.ccw(LatLng(0,0) , LatLng(5,5),LatLng(10,20)) > 0
		False
		
		#Turn right
		>>> ConvexHull.ccw(LatLng( 22.347605,114.060032) , LatLng(22.350513,114.059545),LatLng(22.350044,114.061069)) < 0
		True
		
		#Turn Left
		>>> ConvexHull.ccw(LatLng(22.350513,114.059545),LatLng(22.350044,114.061069), LatLng(22.353305,114.062523)) > 0
		True

		"""
		return (p2.lng - p1.lng)*(p3.lat - p1.lat) - (p2.lat - p1.lat)*(p3.lng - p1.lng)

	ccw = staticmethod(ccw)
	
	def _grahamScan(self):
		"""
		Preform Graham Scan. The result will be stored to ConvexHull.polygon
		
		#Collinear data	
		>>> group = LatLngGroup([(1,1),(5,5),(20,8),(9,9),(10,10)])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(0)
		'(1,1),(20,8),(10,10),(5,5)'

		#Normal data
		>>> group = LatLngGroup([(1,1),(1,10),(10,1),(10,10),(5,5),(6,6),(14,13)])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(0)
		'(1,1),(10,1),(14,13),(1,10)'
		
		#Empty data
		>>> group = LatLngGroup([])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(0)
		''

		#Single data
		>>> group = LatLngGroup([(5,5)])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(0)
		'(5,5)'

		>>> group = LatLngGroup([(10,10),(5,5)])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(0)
		'(10,10),(5,5)'

		>>> group = LatLngGroup([(10,10),(5,5),(3,3)])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(0)
		'(3,3),(10,10),(5,5)'


		>>> group = LatLngGroup([(22.347605,114.060032),(22.350044,114.061069),(22.350513,114.059545),(22.350648,114.059321),(22.351858,114.058679),(22.351858,114.058767),(22.352455,114.059727),(22.353222,114.059484),(22.353305,114.062523),(22.353557,114.060241)])
		>>> LatLngGroup(ConvexHull(group).polygon).toString(6)
		'(22.351858,114.058679),(22.353222,114.059484),(22.353557,114.060241),(22.353305,114.062523),(22.347605,114.060032)'
		"""

		pts = self._sort()
		
		if len(pts) <=3:		
			for i in range(0,len(pts)):
					self.polygon.append(pts[i])	
		else:		
			for i in range(0,2):
					self.polygon.append(pts[i])	
			
			m = 1
			for i in range(2,len(pts)):
				while ConvexHull.ccw( self.polygon[m-1],self.polygon[m] , pts[i] ) >= 0 : #Turn left
					self.polygon = self.polygon[0:-1] #Remove the middle point
					m-=1
				
				self.polygon.append(pts[i])
				m+=1
				
		
	def _find_start(self):
		"""
			Find the starting point for Graham Scan
			>>> group = LatLngGroup([(23,115),(21,115),(24,115)]) 			
			>>> ConvexHull(group)._find_start().toString(0)
			'(21,115)'
			
			>>> group = LatLngGroup([(1,1),(5,5),(20,8),(9,9),(10,10)])
			>>> str(ConvexHull(group)._find_start())
			'(1.000000,1.000000)'
			
		"""
		self.start = self.group.pts[0]	
		
		# Find the the point in most far west-south position
		for pt in self.group.pts:
			if pt.lng < self.start.lng:
				self.start = pt
			elif pt.lng == self.start.lng and pt.lat <  self.start.lat:
				self.start = pt
		
		return self.start

	def _sort(self):
		"""
		Sort the points accroding to the angle from start point. 
		(The order of collinear point is not important)		

		>>> group = LatLngGroup([(1,1),(5,5),(20,8),(9,9),(10,10)]) 			
		>>> LatLngGroup(ConvexHull(group)._sort()).toString(0)
		'(1,1),(20,8),(10,10),(9,9),(5,5)'

		"""
		if len(self.group) >=3:		
			self.start = self._find_start()
			pts = self.group.pts[:]
			ret = sorted(pts,self._compare)
		else:
			ret = self.group.pts[:]
		return ret
		
	def _compare(self,x,y):
		"""
			Compare function for sorting
			
		"""
		if not hasattr(x,"__convexhull_degree__"):
			x.__convexhull_degree__ = self.start.bearing(x)

		if not hasattr(y,"__convexhull_degree__"):
			y.__convexhull_degree__ = self.start.bearing(y)
		
		diff = x.__convexhull_degree__ - y.__convexhull_degree__
		
		if diff < 0:
			return -1
		elif diff > 0:
			return 1
		else:
			return 0	
		
if __name__ == "__main__":
	#group = LatLngGroup()
	#polygon = ConvexHull(group).polygon
	#for pt in polygon:
		#print "%d %d" % (pt.lng , pt.lat)
	#print "%d %d" % (polygon[0].lng , polygon[0].lat)
	
	import doctest
	doctest.testmod(verbose=True)

