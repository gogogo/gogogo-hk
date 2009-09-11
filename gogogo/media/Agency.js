/** Agency
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Agency = function(id){
	gogogo.Model.call(this,id);
    
    /// Polyline from a stop to another (valid for agency with free_transfer service)
    this.polylines = {}
    
    /* 2D array of pseudo trip. Pseudo trip is not existed in the server, it is constructed
     * on the fly that used to store the shortest path from a stop to other.
    */
    this.pseudoTrips = {}
}

extend(gogogo.Agency,gogogo.Model);

gogogo.Agency.prototype.modelType = "agency";

/** Get the name of the agency
 * 
 */

gogogo.Agency.prototype.getName = function() {
    return this.info.name;
}

/** Query the pseudo trip from a stop to another.
 * 
 */

gogogo.Agency.prototype.queryPseudoTrip = function(from,to,callback){
    if (this.pseudoTrips[from] == undefined ) {
        this.pseudoTrips[from] = {};
    }    
    
    if (this.pseudoTrips[from][to] != undefined) {
        if (callback!=undefined)
            callback(this.pseudoTrips[from][to]);
    }

    var agency = this;
  	var api = "/api/agency/path?id=" + this.id +"&from=" + from + "&to=" + to;
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter

    $.getJSON(api, null , function(response) {	
		if (response.stat == "ok") {
            var total = response.data.length;
            var count = 0;
            var stop_id_list = [];
            var trip = new gogogo.Trip();
            
            trip.setStopIDList(response.data);
            agency.pseudoTrips[from][to] = trip;
            if (callback!=undefined)
                callback(trip);
        } 
    });
    
    jQuery.ajaxSettings.cache = cache;	    
}

gogogo.Agency.prototype.createPolyline = function(from,to,stopManager,callback){
    if (this.polylines[from] == undefined ) {
        this.polylines[from] = {};
    }
    
    if (this.polylines[from][to] != undefined) {
        if (callback!=undefined)
            callback(this.polylines[from][to]);
    }
    
    this.queryPseudoTrip(from,to,function(trip){

        trip.queryStops(stopManager,function(trip,stop_list){
            var polyline = trip.createPolyline();                
            agency.polylines[from][to] = polyline;
            if (callback!=undefined)
                callback(polyline);
        });
        
    });
    
}

/** Create an icon according to its transit type
 * 
 */

gogogo.Agency.prototype.createTranitIcon = function() {
    var file;
    var icon;
    switch (this.info.type) {
        case 0:
        case 1:
        case 2: 
            file = "gogogo/markers-transportation/subway.png"
            break;
        case 3: 
            file = "gogogo/markers-transportation/dbus.png"
            break;            
        case 4:
            file = "gogogo/markers-transportation/ferry.png";
            break;
        case 5:
            file = "gogogo/markers-transportation/cablecar.png";
            break;
    }
    
    if (file != undefined){
        
        icon = new GIcon(G_DEFAULT_ICON);
        icon.image = site_data.settings.MEDIA_URL + file;
        icon.iconSize = new GSize(32, 37);
        icon.iconAnchor = new GPoint(16, 32);
        icon.shadow = null;
    }
    return icon;
}
