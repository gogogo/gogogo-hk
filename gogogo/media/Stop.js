
/** Stop
 * 
 * @constructor 
 */

gogogo.Stop = function(json){
	
	this.marker = undefined;
	
	// The object contains complete information of the stop
	this.complete = false
	
	// TRUE if it is querying the complete information of the stop from server
	this.querying = false;
	
	// The ID of the stop
	this.id = undefined;
	
	if (json != undefined){
		this.updateFromJson(json);
	}
	
}

/**
 * Update from JSON
 */

gogogo.Stop.prototype.updateFromJson = function(json){
	var stop = this;
	$.each(["id","name","url","code","agency","geohash","parent_station","desc"] ,function(i,attr){
		if (json[attr]	 != undefined){
			stop[attr] = json[attr];
		}
	});
	
	if (json.latlng != undefined){
		this.latlng = new GLatLng(json.latlng[0], json.latlng[1]);
	}
}

/**
 * Create marker overlay. If it is already created, it will return the created marker.
 */

gogogo.Stop.prototype.createMarker = function(){
	if (this.marker == undefined) {
		var option = {
			"title": this.name
		};
		this.marker = new GMarker(this.latlng,option);
		
		var marker = this.marker;
		var stop = this;
		
		GEvent.addListener(marker,"click",function(){
			html="<object id='markerwin' type='text/html' data='/api/stop/markerwin/" + stop.id + "'> \
			<p>Loading...</p>\
			</object>"
			marker.openInfoWindowHtml(html);
			
		});
	}
	
	return this.marker;
}

/**
 * Query the complete information from server
 */

gogogo.Stop.prototype.query = function(callback) {
	if (this.querying)
		return;
	
	this.querying = true;
	
	api = "/api/stop/get/" + this.id;
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
	var stop = this;
	
	$.getJSON(api, null , function(response) {	
		if (response.stat == "ok"){
			stop.updateFromJson(response.data);
			stop.complete = true;
		}
		if (callback!=undefined)
			callback();
		this.querying = false;
	});
	jQuery.ajaxSettings.cache = cache;	
}
