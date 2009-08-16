/** Map Items Searching Manager
 * 
 * @constructor 
 */

gogogo.SearchingManager = function (map){
	this.map = map;
	
	/// The min zooming for searching 
	this.minZoom = 16;
	
	/// Auto refresh when the map is moved.
	this.autoRefresh = true;

	this.lastBounds = new GLatLngBounds();

	var manager = this;
			
	GEvent.addListener(map, "moveend", function(){
		if (manager.autoRefresh 
			&& manager.map.getZoom() >= manager.minZoom) {
				
			var bounds = manager.getBounds();
			
			if (!bounds.equals(manager.lastBounds)){
				manager.refresh(bounds);	
				manager.lastBounds = bounds;
			}
		}
	});	
}

gogogo.SearchingManager.ceil = function(pt) {
	var f = 50;
	return new GLatLng( Math.ceil(pt.lat() * f ) / f , Math.ceil(pt.lng() * f ) / f )
}

gogogo.SearchingManager.floor = function(pt) {
	var f = 50;
	return new GLatLng( Math.floor(pt.lat() * f ) / f , Math.floor(pt.lng() * f ) / f )
}


/**
 *  Returns the truncated rectangular region of the map view in geographical coordinates.
 */

gogogo.SearchingManager.prototype.getBounds = function() {
	var bounds = this.map.getBounds();

	var sw1 = bounds.getSouthWest();
	var ne1 = bounds.getNorthEast();
	
	var sw2 = gogogo.SearchingManager.floor(sw1);
	var ne2 = gogogo.SearchingManager.ceil(ne1);

	return new GLatLngBounds(sw2,ne2);
}
