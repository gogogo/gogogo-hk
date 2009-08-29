/*
 * gogogo.Planner
 * 
 *  Licensed under Affero GPL v3 (www.fsf.org/licensing/licenses/agpl-3.0.html )
 */

/**  Trip Planner
 * 
 * @constructor
 * Custom events:
 * 
 * clarifyAddress(index,address,response)
 * 
 * tripReady(data)
 * 
 */

gogogo.Planner = function(map,output) {
	this.geocoder = new GClientGeocoder();
    
    this.map = map;
    this.output = output;
	
	/// Array of address point (start , end)
	this.points = [new gogogo.Address(map) , new gogogo.Address(map) ]
	
	this._bindCallback(0);
	this._bindCallback(1);
}

/**
 * Bind the callback to Address object
 */

gogogo.Planner.prototype._bindCallback = function(index){
	var address = this.points[index];
	var planner = this;
	var index = index;

	$(address).bind("clarify",function(event,response) { // Handle clarify event
		$(planner).trigger("clarifyAddress",[index,address,response]);
	});

}

/**
 *  Get address object
 * @param index The index of the address. (0 = start address , 1 = end address)
 */

gogogo.Planner.prototype.getAddress = function(index){
	return this.points[index];
}

/** Clear all the actions that waiting for user's input
 * 
 */

gogogo.Planner.prototype.clearWaitingActions = function() {
    for (var i = 0 ; i < 2; i++){
        this.points[i].clearQueryLocation();
        this.points[i].clearClarifyMarkers();
    }
	
}

/**
 * Suggest the trip from start to end address
 * @param start  
 */

gogogo.Planner.prototype.suggest = function(start,end,callback) {

	this.points[0].setAddress(start);
	this.points[1].setAddress(end);
	var planner = this;
	
	planner.points[0].queryLocation(function(location){
		planner.points[1].queryLocation(function(location) {
			//@TODO - Implement the real trip planner code
			if (callback != undefined) {
				callback(planner.points[0].getAddress(), planner.points[1].getAddress());	
			}
		});
		
	});


}

