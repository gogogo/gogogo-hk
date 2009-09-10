/** Agency
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Agency = function(id){
	gogogo.Model.call(this,id);
    
    /// Polyline from a stop to another (valid for agency with free_transfer service)
    this.polylines = {}
}

extend(gogogo.Agency,gogogo.Model);

gogogo.Agency.prototype.modelType = "agency";

/** Get the name of the agency
 * 
 */

gogogo.Agency.prototype.getName = function() {
    return this.info.name;
}

gogogo.Agency.prototype.createPolyline = function(stopManager,from,to,callback){
    if (this.polylines[from] == undefined ) {
        this.polylines[from] = {};
    }
    
    if (this.polylines[from][to] != undefined) {
        if (callback!=undefined)
            callback(this.polylines[from][to]);
    }
    
    var agency = this;
  	var api = "/api/agency/path?id=" + self.id +"&form=" + from + "&to=" + to;
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter

    $.getJSON(api, null , function(response) {	
		if (response.stat == "ok") {
            var total = response.data.length;
            var count = 0;
            var stop_id_list = [];
            var trip = new gogogo.Trip();
            
            trip.setStopIDList(response.data);
            trip.queryStops(stopManager,function(trip,stop_list){
                var polyline = trip.createPolyline();                
                agency.polylines[from][to] = polyline;
                if (callback!=undefined)
                        callback(polyline);
            });
            
        } 
    });
    
    jQuery.ajaxSettings.cache = cache;	
    
}
