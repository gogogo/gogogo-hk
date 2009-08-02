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

gogogo.Planner = function() {
	this.geocoder = new GClientGeocoder();
	
	/// Array of address point (start , end)
	this.points = [new gogogo.Address() , new gogogo.Address() ]
	
	/// Processing suggestion request
	this.processing = false;
	
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
		planner.processing = false;
		$(planner).trigger("clarifyAddress",[index,address,response]);
	});
	
	$(address).bind("locationChanged",function() {
		if (planner.processing) {
						
			if (index == 0 
				&& planner.points[1].location == undefined ) {

				planner.points[1].queryLocation();

			} else { // index == 1
				$(planner).trigger("tripReady");
				planner.processing = false;
			}
			
		}
	});
}

/**
 *  Get address object
 * @param index The index of the address. (0 = start address , 1 = end address)
 */

gogogo.Planner.prototype.getAddress = function(index){
	return this.points[index];
}

/**
 * Suggest the trip from start to end address
 * @param start  
 */

gogogo.Planner.prototype.suggest = function(start,end) {

	this.processing = true;
	this.points[0].setAddress(start);
	this.points[1].setAddress(end);
	
	if (this.points[0].getLocation() == undefined ) {
		this.points[0].queryLocation();
	} else if (this.points[1].getLocation() == undefined ) {
		this.points[1].queryLocation();
	} else {
		$(this).trigger("tripReady");
		this.processing = false;
	}

}

