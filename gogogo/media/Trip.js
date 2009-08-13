
/** Trip
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Trip = function(id){
	gogogo.Model.call(this,id);
	this.polyline = undefined;
	this.stopObjectList = [];
	this.stopObjectListCount = 0;
}

$.extend(gogogo.Trip,gogogo.Model);

gogogo.Trip.prototype.modelType = "trip";

/**
 * Query a single stop object from StopManager
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
					callback(trip);
				}
			}
		});	
};

/** Query associative stop objects from StopManager
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

gogogo.Trip.prototype.createPolyline = function(options) {
	if (this.polyline != undefined)
		return this.polyline;
		
	if (!this.isStopObjectListComplete())
		return undefined;

	var pts = [];
	for (var i = 0 ; i < this.stopObjectList.length ;i++) {		
	//for (i in this.stopObjectList) {
		if (this.stopObjectList[i] == 'undefined') {
			console.error("Unknown stop - " , this.info.stop_list[i]);
			continue;
		}
		pts[i] = this.stopObjectList[i].latlng;
	}
	
	this.polyline = new GPolyline(pts,this.info.color,5,0.4,options);

	return this.polyline;
}


