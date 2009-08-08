
/** Trip
 * 
 * @constructor 
 */

gogogo.Trip = function(id){

	// The object contains complete information of a trip
	this.complete = false
	
	// TRUE if it is querying the complete information of the trip from server
	this.querying = false;
	
	// The ID of the stop
	this.id = id;
	
	this.stopObjectList = [];
}

/**
 * Update from JSON
 */
gogogo.Trip.prototype.updateFromJson = function(json){
	var trip = this;
	$.each(["direction","short_name","service","route","headsign","shape","stop_list"] ,function(i,attr){
		if (json[attr]	 != undefined){
			trip[attr] = json[attr];
		}
	});
}

/**
 * Query the complete information from server
 */

gogogo.Trip.prototype.query = function(callback) {
	if (this.querying)
		return;
	
	this.querying = true;
	
	api = "/api/trip/get/" + this.id;
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
	var	trip = this;
	
	$.getJSON(api, null , function(response) {	
		if (response.stat == "ok"){
			
			trip.updateFromJson(response.data);
			trip.complete = true;
			console.log(trip);
		}
		if (callback!=undefined)
			callback(trip);
		this.querying = false;
	});
	jQuery.ajaxSettings.cache = cache;	
}

/** Query associative stop objects from StopManager
 * 
 */

gogogo.Trip.prototype.queryStops = function (manager) {
	
	if (this.stop_list == undefined) {
		return ;
	}

	var trip = this;
	
	$(manager).bind("stopComplete",function(e,stop) { 
		console.log("stopComplete",stop);
		for (var i = 0 ; i < trip.stop_list.length ;i++) {
			
			if (trip.stop_list[i] == stop.id){
				trip.stopObjectList[i] = stop;
				if (trip.isStopObjectListComplete())
					$(trip).trigger("stopObjectListComplete");
				break;
			}
		}
		
	});

	
	for (var i = 0 ; i < this.stop_list.length ;i++) {
		var stop = manager.queryStop(this.stop_list[i]);
		
		if (stop != undefined){
			this.stopObjectList[i] = stop;
			if (this.isStopObjectListComplete())
				$(this).trigger("stopObjectListComplete");
		}
	}
}

/** Check is all the stop objects received.
 * 
 */
gogogo.Trip.prototype.isStopObjectListComplete = function () {

	var ret;
	if (this.stopObjectList.length == this.stop_list.length){		
		ret =true;
	} else {
		ret = false;
	}
	console.log(this.stopObjectList.length,ret);	
	
	return ret;
}

gogogo.Trip.prototype.createPolyline = function(options) {
	if (this.polyline != undefined)
		return this.polyline;
		
	if (!this.isStopObjectListComplete())
		return undefined;
	
	var pts = []
	
	for (var i = 0 ; i < this.stopObjectList.length ;i++) {		
		pts[i] = this.stopObjectList[i].latlng;
	}
	console.log(pts);
	this.polyline = new GPolyline(pts,"#000000",5,0.5,options);

	return this.polyline;
}
