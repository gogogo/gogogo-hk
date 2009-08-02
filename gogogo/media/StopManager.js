/*
 * gogogo.StopManager
 *
 *  Licensed under Affero GPL v3 (www.fsf.org/licensing/licenses/agpl-3.0.html )
 */

/** Stop Manager
 * 
 * @constructor 
 */

gogogo.StopManager = function (map){
	this.minZoom = 15;
		
	this.map = map;
	
	// Stop dictionary
	this.stops = new Object();
	
	var options = { borderPadding: 50, trackMarkers: true };
	
	this.markermanager = new MarkerManager(map,options);
	
	manager = this;

	GEvent.addListener(map, "moveend", function(){
		manager.refresh();
	});	
	
};

/** Refresh the stop list from gogogo server.
 * 
 */

gogogo.StopManager.prototype.refresh = function() {
	
	zoom = this.map.getZoom();
	
	if (zoom < this.minZoom)
		return;	
	
	bounds = this.map.getBounds();
	api = "/api/stop/search/" + 
		bounds.getNorthEast().lat() + "," + bounds.getNorthEast().lng() + ","	+
		bounds.getSouthWest().lat() + "," + bounds.getSouthWest().lng();
	
	manager = this;
	
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
	$.getJSON(api, null , function(data) {
		if (data.stat == "ok") {
			$.each(data.data, function(i, item){
				if (manager.stops[item.id] == undefined ) {
					var point = new GLatLng(item.latlang[0], item.latlang[1]);
					var option = {
                        "title": item.name
                   	};
                   	marker = new GMarker(point,option);
                 
                	manager.markermanager.addMarker(marker,manager.minZoom);
                	manager.stops[item.id] = item;
				}
			});
			manager.markermanager.refresh();
		}
	});
	jQuery.ajaxSettings.cache = cache;	
		
}


