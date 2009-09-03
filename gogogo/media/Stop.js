
/** Stop
 *
 * @constructor
 * @base gogogo.Model
 */

gogogo.Stop = function(id){
    gogogo.Model.call(this,id);

    this.marker = undefined;

}

extend(gogogo.Stop , gogogo.Model)

//$.extend(gogogo.Stop , gogogo.Model) // Can not be used  updateFromJson() will raise "too much recursion"

gogogo.Stop.prototype.modelType = "stop";

/**
 * Update from JSON
 */

gogogo.Stop.prototype.updateFromJson = function(json){

    gogogo.Model.prototype.updateFromJson.call(this,json);

    if (json.latlng != undefined) {
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

        GEvent.addListener(marker,'infowindowopen',function(){
			var cache = jQuery.ajaxSettings.cache;
			jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter			
            $('#markerwin').load(
                '/api/stop/markerwin/' + stop.id, null,
                function(){
                    var win = map.getInfoWindow();
                    var content = $('#markerwin');
                    win.reset(
                        win.getPoint(), win.getTabs(),
                        new GSize(content.width(), content.height()),
                        null, null
                    );
                }
            );
            jQuery.ajaxSettings.cache = cache;	
            
        });

        GEvent.addListener(marker,"click",function(){
            marker.openInfoWindowHtml('<div id="markerwin">Loading...</div>');
        });
    }

    return this.marker;
}

/** Return a GLatLng instance of the location of the stop
 * 
 */

gogogo.Stop.prototype.getLatLng  = function(){
    return this.latlng;
}

/** Get the name of the stop
 * 
 */

gogogo.Stop.prototype.getName = function(){
    return this.info.name;
}
