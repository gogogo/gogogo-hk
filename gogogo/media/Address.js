/** Address
 * 
 * @constructor
 */

gogogo.Address = function(text) {
	
	this.text = text; // The text address
	 
	this.location ;  // The location of address (GLatLng)
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

/** Query the location 
 * 
 */
gogogo.Address.prototype.queryLocation = function(geocoder) {
	var address = this;
	
	if (this.text == undefined || this.text == ""){
		$(address).trigger("clarify");
		return;
	}

	gogogo.Address.geocoder.getLocations(this.text, function(response) {
				
		if (response.Status.code == 200 && response.Placemark.length == 1) {
			address.setLocation ( new GLatLng(response.Placemark[0].Point.coordinates[1], 
										   response.Placemark[0].Point.coordinates[0]) );
			
		} else {
			
			/// Request for clarify.
			$(address).trigger("clarify",response);
		}
	});	

}
