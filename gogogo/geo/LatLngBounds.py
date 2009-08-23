import math
from LatLng import LatLng

class LatLngBounds:
    """
    A rectangle in geographical coordinates, excluding that crosses the 180 degrees meridian.
    """
    
    def __init__(self,sw= None, ne = None):
        """
        @type sw LatLng
        @type ne LatLng
        """
        self.sw = sw
        self.ne = ne
        
    def containsLatLng(self,latlng):
        """
        Returns true if the geographical coordinates of the point lie within this rectangle.
        
        >>> bounds = LatLngBounds( LatLng(-0.25, 51.5) , LatLng(0.1, 52.5) )
        >>> bounds.containsLatLng(LatLng(-0.3,52))
        False
        >>> bounds.containsLatLng(LatLng(-0.2,52))
        True
                
        """

        if (self.sw.lat <= latlng.lat and latlng.lat <= self.ne.lat and
            self.sw.lng <= latlng.lng and latlng.lng <= self.ne.lng ):
            return True
        return False

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)

