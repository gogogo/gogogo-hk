
/** Stop
 * 
 * @constructor 
 */

gogogo.Stop = function(json){
	
	this.marker = undefined;
	
	if (json != undefined){
		this.updateFromJson(json);
	}
	
}

/**
 * Update from JSON
 */

gogogo.Stop.prototype.updateFromJson = function(json){
	var stop = this;
	$.each(["id","name","url"] ,function(i,attr){
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
			console.log(html);
			marker.openInfoWindowHtml(html);
			
		});
	}
	
	return this.marker;
}
