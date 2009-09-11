/** Address query and marker management class
 * 
 * @constructor
 * 
 * @param map A GMap instance
 * @param name The name of the address (e.g "A" , "B")
 */

gogogo.Address = function(map,name) {
    
    this.map = map;
    
    this.name = name;
	
	this.text; // The text address
	 
	this.location ;  // The location of address (GLatLng)
    
    // Marker of the address in map
    this.locationMarker;
    
    // If more than one address is found on queryLocation , 
    // it will store all the address returned.
    this._possibleAddress = [];
    
    var options = { borderPadding: 50, trackMarkers: false };
	
	this.markermanager = new MarkerManager(map,options);
}

gogogo.Address.geocoder = undefined;

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
    
    if (this.locationMarker == undefined) {
        this.locationMarker = this._createMarker();
        this.map.addOverlay(this.locationMarker);
    } else {
        this.locationMarker.setLatLng(this.location);
    }
    
	$(this).trigger("locationChanged");
}

/** Return TRUE if the input address is a latlng pair
 * 
 */
gogogo.Address.prototype.parseLatLngAddress = function (ret) {
    var res = false;
    var items = this.text.split(",");
    if (items.length == 2) {
        res = true;
        for (var i = 0 ; i < 2 ; i++) {
            ret[i] = parseFloat(items[i]);
            if (ret[i] == NaN){
                res = false;
                break;
            }
        }
    }   
        
    return res;
}

/** Query the location from assigned text address
 * 
 * @param callback The callback to be involved. 
 */
gogogo.Address.prototype.queryLocation = function(callback) {
    if (gogogo.Address.geocoder == undefined ) {
        gogogo.Address.geocoder = new GClientGeocoder();
        gogogo.Address.geocoder.setBaseCountryCode(gogogo.COUNTRY_CODE);        
        
        var sw = new GLatLng(gogogo.BOUNDARY_BOX[0],gogogo.BOUNDARY_BOX[1]);
        var ne = new GLatLng(gogogo.BOUNDARY_BOX[2],gogogo.BOUNDARY_BOX[3]);
        var bounds = new GLatLngBounds(sw,ne);
        
        gogogo.Address.geocoder.setViewport(bounds);        
    }

	var address = this;
    
    var latlng = [];
    if (this.location == undefined && this.parseLatLngAddress(latlng) ){
        this.setLocation( new GLatLng(latlng[0],latlng[1])) ;
    }
	
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

    this._possibleAddress = []
	gogogo.Address.geocoder.getLocations(this.text, function(response) {
				
		if (response.Status.code == 200 && response.Placemark.length == 1) {
			var pt = new GLatLng(response.Placemark[0].Point.coordinates[1], 
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

/** Get the location of icon file for clarify marker with index 
 * 
 */

gogogo.Address.getMarkerIconFile = function(index){
    var icon = site_data.settings.MEDIA_URL + 
        "gogogo/markers/iconb" + 
        (index + 1 )+ 
        ".png";
            
    return icon;
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
        
        var icon = new GIcon();
        icon.image = gogogo.Address.getMarkerIconFile(i);
        icon.iconSize = new GSize(20, 34);
        icon.iconAnchor = new GPoint(10, 30);
        
        var option = {
            "title": address.text,
            "icon" : icon
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

/** Clear all the clarify markers
 * 
 */

gogogo.Address.prototype.clearClarifyMarkers = function() {
    this.markermanager.clearMarkers();
}

/**
 * Create a marker to indicate the location of the address
 */

gogogo.Address.prototype._createMarker = function() {
    var point = this.getLocation();
    if (point == undefined)
        return null;
    
    var icon = new GIcon(G_DEFAULT_ICON);
    icon.image = site_data.settings.MEDIA_URL + 
        "gogogo/markers/paleblue_Marker" + this.name + ".png";
    icon.iconSize = new GSize(20, 34);
    icon.iconAnchor = new GPoint(10, 30);
    
    var option = {
        "icon" : icon,
        "draggable" : true
    };
    
    marker = new GMarker(point,option);   
    
    var address = this;
    
    GEvent.addListener(marker, "dragend", function(latlng){
        
        gogogo.Address.geocoder.getLocations(latlng, function(response) {
            if (response.Status.code == 200 ){
                address.setAddress(response.Placemark[0].address);
            } else {
                address.setAddress(latlng.lat() + ","  + latlng.lng());
            }
            address.setLocation(latlng);
        });
        
    });
    
    return marker; 
}
