/*
 * gogogo.map
 *
 *  Licensed under Affero GPL v3 (www.fsf.org/licensing/licenses/agpl-3.0.html )
 */

gogogo.StopManager = function (map){
	
	this.map = map;
	
	// Stop dictionary
	this.stops = new Object();
	
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
	if (zoom <= 15)
		return;	
	
	bounds = this.map.getBounds();
	api = "/api/stop/search/" + 
		bounds.getNorthEast().lat() + "," + bounds.getNorthEast().lng() + ","	+
		bounds.getSouthWest().lat() + "," + bounds.getSouthWest().lng();
	
	manager = this;
	
	$.getJSON(api, null , function(data) {
		if (data.stat == "ok") {
			$.each(data.data, function(i, item){
				if (manager.stops[item.id] == undefined ) {
					var point = new GLatLng(item.latlang[0], item.latlang[1]);
					var option = {
                        "title": item.name
                   	};
                   	option.title = item.name;
                 
                	manager.map.addOverlay(new GMarker(point), option);
                	manager.stops[item.id] = item;
                	count ++;
				}
			});
		}
	});	
		
}


