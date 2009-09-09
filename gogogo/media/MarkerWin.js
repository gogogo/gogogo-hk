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

gogogo.MarkerWin.generalTemplate = "\
${stop_name} <span class='stop_parent'></span> <br> \
${agency_name}";

gogogo.MarkerWin.prototype.renderGeneral = function(target) {
    var t = $.template(gogogo.MarkerWin.generalTemplate);
    $(target).empty();
    $(target).append(t,{
      stop_name : this.stop.getName()
    });
    
    var stop_parent = $(target).find(".stop_parent");
    this.stop.getParentStation(this.stopManager,function(station){
        if (station != undefined){
            $(stop_parent).append(" : " + station.getName());
        }
    });
    
    
}
