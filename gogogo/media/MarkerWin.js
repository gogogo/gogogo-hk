/** Marker Window - Handle transit information query in the info window of marker
 * 
 *
 * @constructor 
 */

gogogo.MarkerWin = function (map,stop,marker,modelManager,stopManager) {
    this.map = map;
    this.stop = stop;
    this.marker = marker;
    this.modelManager = modelManager;
    this.stopManager = stopManager;
    
    var markerWin = this;
    
    GEvent.addListener(marker,'infowindowopen',function(){
        markerWin.renderGeneral('#markerwin');
        /*
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
        */
    });
    
    
    GEvent.addListener(marker,"click",function(){
        marker.openInfoWindowHtml("<div id='markerwin'>Loading...</div>");
    });
}

gogogo.MarkerWin.prototype.resize = function() {
    var win = this.map.getInfoWindow();
    var content = $('#markerwin');
    
    win.reset(
        win.getPoint(), win.getTabs(),
        new GSize(content.width(), content.height()),
        win.getPixelOffset(), null
    );    
}

gogogo.MarkerWin.generalTemplate = "\
${stop_name} <span class='stop_parent'></span> <br> \
<span class='agency_name'></span> <p>\
<div class='trip_list'></div>";

gogogo.MarkerWin.tripListTemplete = "\
<span class='trip'>${code}(${headsign})</span> \
";

gogogo.MarkerWin.prototype.renderGeneral = function(target) {
    var t = $.template(gogogo.MarkerWin.generalTemplate);
    $(target).empty();
    $(target).append(t,{
      stop_name : this.stop.getName()
    });
    
    var stop_parent = $(target).find(".stop_parent");
    this.stop.queryParentStation(this.stopManager,function(station){
        if (station != undefined){
            $(stop_parent).append(" : " + station.getName());
        }
    });
    
    var agency_name = $(target).find(".agency_name");
    this.stop.queryAgency(this.modelManager,function(agency){
       if (agency != undefined){
           $(agency_name).append(agency.getName());
       } 
    });   
    
    var trip_list = $(target).find(".trip_list");
    this.renderTripList(trip_list);
}

gogogo.MarkerWin.prototype.renderTripList = function(target) {
    var markerWin = this;
    var cache = jQuery.ajaxSettings.cache;
    
    jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter			
    var api = "/api/stop/list_trip?id=" + this.stop.getID();
    
    $.getJSON(api, null , function(response) {	
        if (response.stat == "ok"){
            
            $.each(response.data,function(i,trip_id) {
                var div = $("<span></span>");   
                $(target).append(div);
                markerWin.modelManager.queryTrip(trip_id,function(trip){
                    var t = $.template(gogogo.MarkerWin.tripListTemplete);
                    $(div).append(t,{
                        code : trip.getName(),
                        headsign : trip.getHeadsign()    
                    });
                    
                });
            });
            
            markerWin.resize();
        }
    });
    jQuery.ajaxSettings.cache = cache;	            
}
