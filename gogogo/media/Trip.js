
/** Trip
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Trip = function(id){
	gogogo.Model.call(this,id);
	this.polyline = undefined;
    
    // Stop Object storage
	this.stopObjectList = [];
    
    // No. of stop objects stored
	this.stopObjectListCount = 0;
}

$.extend(gogogo.Trip,gogogo.Model);

gogogo.Trip.prototype.modelType = "trip";

/**
 * Query a single stop object from StopManager
 * 
 * @param manager Either of StopManager or ModelManager
 */

gogogo.Trip.prototype._queryStop = function(manager,index,callback){
	var trip = this;	
	manager.queryStop(this.info.stop_list[index],
		function(stop) {					
			trip.stopObjectList[index] = stop;
			trip.stopObjectListCount++;
			if (trip.isStopObjectListComplete()) {
				$(trip).trigger("stopObjectListComplete");
				if (callback !=undefined){
					callback(trip,trip.stopObjectList);
				}
			}
		});	
};

/** Query associated stop objects from StopManager
 * 
 * @param manager Either of StopManager or ModelManager
 * @param callback To be involved when all the objects are fetched from server. ( callback(trip,stop_list) )
 * 
 */

gogogo.Trip.prototype.queryStops = function (manager,callback) {
	
	if (this.info.stop_list == undefined) {
		return ;
	}

	this.stopObjectListCount = 0;
	
	for (var i = 0 ; i < this.info.stop_list.length ;i++) {
		this._queryStop(manager,i,callback);
	}
}

/** Check is all the stop objects received.
 * 
 */
gogogo.Trip.prototype.isStopObjectListComplete = function () {

	var ret;
	if (this.stopObjectListCount == this.info.stop_list.length){		
		ret =true;
	} else {
		ret = false;
	}

	return ret;
}

/** Clear all the stop stored
 * 
 */

gogogo.Trip.prototype.clearStops = function(){
    this.info.stop_list = [];
    
	this.stopObjectList = [];
   
	this.stopObjectListCount = 0;    
}

/** Get the stop ID list
 * 
 */

gogogo.Trip.prototype.getStopIDList = function(id_list) {
    return this.info.stop_list;
}

/** Set the stop ID list
 * 
 * In generic , user should not call this function as the stop 
 * list should be get from server. The only exception is , the 
 * trip instance is pseudo which is not real. Pseudo trip is 
 * mainly used in constructing temp polyline objects based 
 * on stop list
 * 
 * @see gogogo.Agency.createPolyline()
 * 
 */

gogogo.Trip.prototype.setStopIDList = function(stop_list){
    this.clearStops();   
    this.info.stop_list = stop_list;
}

/** Get the list of gogogo.Stop object
 * 
 */

gogogo.Trip.prototype.getStopList = function(){
    return this.stopObjectList;
}


/**
 * Get polyline
 */

gogogo.Trip.prototype.getPolyline = function(options) {
	return this.polyline;
}

gogogo.Trip.prototype.createPolyline = function(options) {
	if (this.polyline != undefined)
		return this.polyline;
		
	if (!this.isStopObjectListComplete())
		return undefined;

	var pts = [];
	for (var i = 0 ; i < this.stopObjectList.length ;i++) {		
	//for (i in this.stopObjectList) {
		if (this.stopObjectList[i] == 'undefined' || this.stopObjectList[i].error) {
			//console.error("Unknown stop - " , this.info.stop_list[i]);
			continue;
		}
		pts[i] = this.stopObjectList[i].latlng;
	}
	
	this.polyline = new GPolyline(pts,this.info.color,5,0.4,options);

	return this.polyline;
}

/** Remove the polyline (p.s it is not removed from map)
 */
gogogo.Trip.prototype.removePolyline = function() {
    this.polyline = undefined;
}

/** Get the bounding region
 * 
 */

gogogo.Trip.prototype.getBounds = function(){
    var bounds = new GLatLngBounds();    
    if (this.stopObjectListCount > 0){
        
        
        for (var i =0 ; i < this.stopObjectList.length; i++){
            var stop = this.stopObjectList[i];
            if (!stop.error)
                bounds.extend(stop.getLatLng());
        }
    }
    
    return bounds;
}

/** Zoom and pan to the trip
 *
 */

gogogo.Trip.prototype.zoomAndPan = function(map){
    if (this.stopObjectListCount > 0){
        var bounds = new GLatLngBounds();
        
        for (var i =0 ; i < this.stopObjectList.length; i++){
            var stop = this.stopObjectList[i];
            if (!stop.error)
                bounds.extend(stop.getLatLng());
        }
    
        if (!bounds.isEmpty()){
            var center = bounds.getCenter();
            var zoom = map.getBoundsZoomLevel(bounds);
            map.setCenter(center,zoom);
		}
    }
}

/** Get the name of the trip
 * 
 */

gogogo.Trip.prototype.getName = function() {
    return this.info.name;
}

/** Get the headsign of the trip
 * 
 */

gogogo.Trip.prototype.getHeadsign = function() {
    return this.info.headsign;
}
