/** Address
 * 
 * @constructor
 */

gogogo.Address = function(map,output) {
    
    this.map = map;
    
    this.output = output;
	
	this.text; // The text address
	 
	this.location ;  // The location of address (GLatLng)
    
    this._possibleAddress = [];
    
    var options = { borderPadding: 50, trackMarkers: false };
	
	this.markermanager = new MarkerManager(map,options);
}

gogogo.Address.geocoder = new GClientGeocoder();

/** Set the address. If the new address do not match with the old address,
 * the location of previous address will be cleared.
 * 
 */

gogogo.Address.prototype.setAddress = function(text){
	
	if (this.text != text) {
		this.text = text;
		this.location = undefined;
		$(this).trigger("addressChanged");
	}
	this.text = text;
}

/**
 * Get the address
 */

gogogo.Address.prototype.getAddress  = function(){
	return this.text
}

/**
 * @return "undefined" or a GLatLng object of the address
 */

gogogo.Address.prototype.getLocation = function(){
	return this.location;
}

gogogo.Address.prototype.setLocation = function(pt) {
	this.location = pt;
	$(this).trigger("locationChanged");
}

/** Query the location from assigned text address
 * 
 * @param callback The callback to be involved. 
 */
gogogo.Address.prototype.queryLocation = function(callback) {
	var address = this;
	
	if (this.location != undefined){
		if (callback != undefined) {
			callback(this.location);
		}
		return this.location;
	}
	
	if (callback!=undefined) {
		$(address).one("locationChanged",function (e){
			$(address).trigger("_queryLocation");
		});
		
		$(address).one("_queryLocation",function (e){ // can be cancelled by clearQueryLocation()
			callback(address.location);
		});
	}
			
	if (this.text == undefined || this.text == ""){
		// Request for clarify
		$(address).trigger("clarify");
		return;
	}

    this._possibleAddress = []
	gogogo.Address.geocoder.getLocations(this.text, function(response) {
				
		if (response.Status.code == 200 && response.Placemark.length == 1) {
			pt = new GLatLng(response.Placemark[0].Point.coordinates[1], 
										   response.Placemark[0].Point.coordinates[0]);
			address.setLocation ( pt );
			
		} else {
            if (response.Status.code != 200 ) {

                /// The address is unknwon
                $(address).trigger("unknown",response);
                
            } else {
                
                $(response.Placemark).each(  function(i,place){
                    var point = new GLatLng(place.Point.coordinates[1],place.Point.coordinates[0]);
                    var textAddr = place.address;
                    address._possibleAddress.push([textAddr,point]);
                });
                
			/// Request for clarify.
			$(address).trigger("clarify",response);

            }
		}
	});	
	
	return undefined;

}

/** Unbind all callback that is pass to queryLocation()
 * 
 */

gogogo.Address.prototype.clearQueryLocation = function() {
	$(this).unbind("_queryLocation");
}

/** Create markers for available choice of address
 * 
 */
gogogo.Address.prototype.createClarifyMarkers = function(){
    var address = this;
    var bounds = new GLatLngBounds();
    
    $(address._possibleAddress).each(function (i,item){
        var textAddr = item[0];
        var point = item[1];
        var option = {
            "title": address.text
        };
        marker = new GMarker(point,option);
        bounds.extend(point);
        
        // Visible for all the level
        address.markermanager.addMarker(marker,1); 
    });
    
    if (!bounds.isEmpty()){
        var center = bounds.getCenter();
        var zoom = map.getBoundsZoomLevel(bounds);
        map.setCenter(center,zoom);
    }
}

gogogo.Address.prototype.clearClarifyMarkers = function() {
    this.markermanager.clearMarkers();
}
