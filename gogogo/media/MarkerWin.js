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
<a class='trip'>${code}(${headsign})</a> \
";

gogogo.MarkerWin.agencyTemplate = "\
<table> \
<tr><td>Name : </td><td>${name}</td></tr>\
<tr><td>Type : </td><td>${type}</td></tr>\
<tr><td>Icon : </td><td>${icon}</td></tr>\
<tr><td>URL : </td><td>${url}</td></tr>\
<tr><td>Phone : </td><td>${phone}</td></tr>\
</table>\
<a class='back'>Back</a> \
<!-- \
<a href='#'  target='_blank'>Detail View</a>\
//--> \
";

gogogo.MarkerWin.tripTemplate = "\
<b>${name}</b>\
<ol class='stop_list'>\
</ol>\
<a class='back'>Back</a> \
"


gogogo.MarkerWin.prototype.renderGeneral = function(target) {
    var markerWin = this;
    var t = $.template(gogogo.MarkerWin.generalTemplate);
    $(target).empty();
    $(target).append(t,{
      stop_name : this.stop.getName()
    });
    
    var stop_parent = $(target).find(".stop_parent");
    this.stop.queryParentStation(this.stopManager,function(station){
        if (station != markerWin.stop){
            $(stop_parent).append(" : " + station.getName());
        }
    });
    
    var agency_name = $(target).find(".agency_name");
    this.stop.queryAgency(this.modelManager,function(agency){
       if (agency != undefined){
           var a = $("<a> " + agency.getName() + " </a>");
           $(agency_name).append(a);
           $(a).click(function(){
               markerWin.renderAgencyInfo(target,agency);
           });
       } 
    });   
    
    var trip_list = $(target).find(".trip_list");
    this.renderTripList(trip_list,target);
}

gogogo.MarkerWin.prototype.renderTripList = function(target,content) {
    var markerWin = this;
    var cache = jQuery.ajaxSettings.cache;
    
    jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter			
    var api = "/api/stop/list_trip?id=" + this.stop.getID();
    
    $.getJSON(api, null , function(response) {	
        if (response.stat == "ok"){
            var total = response.data.length;
            var count = 0;
            $.each(response.data,function(i,trip_id) {
                var div = $("<span></span>");   
                $(target).append(div);
                markerWin.modelManager.queryTrip(trip_id,function(trip){
                    var t = $.template(gogogo.MarkerWin.tripListTemplete);
                    $(div).append(t,{
                        code : trip.getName(),
                        headsign : trip.getHeadsign()    
                    });
                    
                    $(div).click(function(){
                        markerWin.renderTrip(content,trip);
                    });
                    
                    count++;
                    if (count == total){
                        markerWin.resize();
                    }
                });
            });
            
            markerWin.resize();
        }
    });
    jQuery.ajaxSettings.cache = cache;	            
}

/** Render agency page
 * 
 */
gogogo.MarkerWin.prototype.renderAgencyInfo = function(target,agency){
    $(target).empty();
    var t = $.template(gogogo.MarkerWin.agencyTemplate); 
    var markerWin = this;
    $(target).append(t,{
      name : agency.getName(),
      url : agency.info.url,  
      type : agency.info.type,
      phone : agency.info.phone,
    });
    
    markerWin.resize();    
    
    $(target).find(".back").click(function (){
        markerWin.renderGeneral(target);
    });
}

/** Render trip information
 * 
 */

gogogo.MarkerWin.prototype.renderTrip = function(target,trip){
    $(target).empty();
    var t = $.template(gogogo.MarkerWin.tripTemplate); 
    var markerWin = this;
    
    $(target).append(t,{
       name : trip.getName()
    });

    markerWin.resize();

    $(target).find(".back").click(function (){
        markerWin.renderGeneral(target);
    });
    
    var parent_station = this.stop.queryParentStation(); // Already called in renderGeneral
    
    trip.queryStops(this.stopManager , function(trip,stop_list){
        var stop_list_div = $(target).find(".stop_list");
        var found_current_stop = false;
        $.each(stop_list,function(i,stop){
            var li = $("<li>" + stop.getName() + "</li>");
            
            if (stop.getID() ==  parent_station.getID() || stop.getID() == markerWin.stop.getID() ){
                li.addClass("current_stop");
                found_current_stop = true;
            } else if (!found_current_stop) {
                li.addClass("before");
            } else {
                li.addClass("after");
            }
            
            $(stop_list_div).append(li);
        });
        
        markerWin.resize();
    });

}
