
/** Trip
 * 
 * @constructor 
 * @extends gogogo.Model
 * @base gogogo.Model
 */

gogogo.Trip = function(id){
	gogogo.Model.call(this,id);
	
	this.stopObjectList = [];
}

$.extend(gogogo.Trip,gogogo.Model);

gogogo.Trip.prototype.modelType = "trip";

/** Query associative stop objects from StopManager
 * 
 */

gogogo.Trip.prototype.queryStops = function (manager) {
	
	if (this.info.stop_list == undefined) {
		return ;
	}

	var trip = this;
	
	$(manager).bind("stopComplete",function(e,stop) { 
		console.log("stopComplete",stop);
		for (var i = 0 ; i < trip.info.stop_list.length ;i++) {
			
			if (trip.info.stop_list[i] == stop.id){
				trip.stopObjectList[i] = stop;
				if (trip.isStopObjectListComplete())
					$(trip).trigger("stopObjectListComplete");
				break;
			}
		}
		
	});

	
	for (var i = 0 ; i < this.info.stop_list.length ;i++) {
		var stop = manager.queryStop(this.info.stop_list[i]);
		
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
	if (this.stopObjectList.length == this.info.stop_list.length){		
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

	this.polyline = new GPolyline(pts,"#000000",5,0.5,options);

	return this.polyline;
}


