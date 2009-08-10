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
	
	/// The min zoom of stop markers
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
					var stop = new gogogo.Stop(item.id);
					stop.updateFromJson(item);
					var marker = stop.createMarker();
                 
                	manager.markermanager.addMarker(marker,manager.minZoom);
                	manager.stops[item.id] = stop;
				}
			});
			manager.markermanager.refresh();
		}
	});
	jQuery.ajaxSettings.cache = cache;	
		
}

/** Get stop
 * 
 * @return A stop object instance with complete information or undefined if it is not queryed.
 */
gogogo.StopManager.prototype.getStop = function(id) {
	stop = this.stops[id];
	if (stop != undefined) {
		if (stop.complete == false)
			stop = undefined;
	}
	return stop;
}

/**
 * Query the stop from database
 * 
 * Signals:
 * 
 * stopComplete - A stop's query() operation is completed.
 * 
 * @param id The id of the stop
 * @param callback The callback to be involved after the query complete. Only a single argument of the model instance is passed
 * 
 * @return If the stop is already queryed , it will return the object. Otherwise, it will return undefined.
 * 
 */

gogogo.StopManager.prototype.queryStop = function(id,callback) {
	var stop = this.getStop(id);
	
	if (stop == undefined) {
		if (this.stops[id] == undefined){
			this.stops[id] = new gogogo.Stop();
			this.stops[id].id = id;
		}
		stop = this.stops[id];
		
		if (stop.complete == false && !stop.querying ){
			var manager = this;		
			stop.query(function(stop){
				$(manager).trigger("stopComplete",stop);
			});
		}
		
		if (callback!=undefined)
			stop.query(callback);
		
		return undefined;
		
	}  else {
		
		if (callback!=undefined)
			callback(stop)
		
		return stop;
	}
}
