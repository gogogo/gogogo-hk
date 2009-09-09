/** TransitPlan
 * 
 * Transit trip planning
 *
 * @constructor 
 */

gogogo.TransitPlan = function (json) {
    this.fare = json.fare;
    
    /* Example format of transits
     * 
      [
        { 
          agency: 
          trip : 
          on :
          off :
         }
         , 
         ....
      ]
     */
    
    this.transits = json.transits;
    
    /// Array of overlays created by createOverlays
    this.overlays = undefined;
    
}

/** Get an array of ID for each transit
 * 
 */

gogogo.TransitPlan.prototype.getTransitIDList = function() {
    var ret = [];
    
    for (var i = 0 ; i < this.transits.length ;i++){
        var transit = this.transits[i];
        var item = [];
        item[0] = transit.agency;
        item[1] = transit.trip;
        ret.push(item);
    }
    
    return ret;
}

/** Produce a DIV element to display the transit plan
 * 
 * @param num The number of the plan
 */

gogogo.TransitPlan.prototype.createDiv = function(num,map,modelManager,stopManager) {
    var transit_plan_div = $("<div class='transit_plan' ></div>");
    var template = "\
    <div class='transit_op'>${transit_op}</div> \
    <div class='index'>${index}.</div> \
    <div class='fare'>${fare}</div> \
    <div class='transit_list'>${transit_list}</div> \
" ; 

    var plan = this;
    var id_list = this.getTransitIDList();
    var map_link = "<a>Map</a>";
    var transit_op = map_link;
    var fare = "$" + this.fare;

    var render= $.template(template);
    $(transit_plan_div).append(render,{
       "index" : num,
       "fare" : fare,
       "transit_op" : "<a>Map</a>"
    });

    var transit_op = $(transit_plan_div).children(".transit_op");
    
    var map_link = $(transit_plan_div).find("a");
       
    $(map_link).click( function(){
        plan.createOverlays(stopManager,function(overlays){
            $.each(overlays,function(i,overlay){
                map.addOverlay(overlay);
            });

        });
    });
    
    var transit_list_div = $(transit_plan_div).children(".transit_list");
        
    $.each(id_list,function(i,id)  {
        var div = $("<div></div>");
        var agency_span = $("<span></span>");
        
        $(transit_list_div).append(div);
        $(div).append(agency_span);
        $(agency_span).append(id[0]);
        
        modelManager.queryAgency(id[0],function(agency){
            $(agency_span).empty();
            $(agency_span).append(agency.getName());
        });
        
        if (id[1] != undefined ){
            var trip_span = $("<span></span>");
            $(div).append(" ");
            $(div).append(trip_span);
            $(trip_span).append(id[1]);
            
            modelManager.queryTrip(id[1],function(trip){
                $(trip_span).empty();
                $(trip_span).append(trip.getName());
            });
        }
        
    });
    
    return transit_plan_div;
}

gogogo.TransitPlan.prototype.createOverlays = function(stopManager,callback) {
    if (this.overlays != undefined) {
        callback(this.overlays);
        
        return this.overlays;
    }
    
    this.overlays = [];
    
    var id_list = this.getTransitIDList();        
    var total = id_list.length;
    var removed_trip = 0
    var count = 0;
    var plan = this;

    $.each(id_list,function(i,id)  {
        
        if (id[1]!=undefined) {
                    
            modelManager.queryTrip(id[1],function(trip){
              if (!trip.error){
                  trip.queryStops(stopManager,function(){
                      var polyline = trip.createPolyline();
                      plan.overlays.push(polyline);
                    
                       count++;
                       
                       if (count == total){
                           callback(plan.overlays);
                       }

                  });
              } else {
                  // The trip ID not found.
                  count ++;
                  if (count == total){
                      callback(plan.overlays);
                  }
              }                
            });
            
        } else { // No trip info
            count++;
            if (count == total){
              callback(plan.overlays);
            }            
        }
        
    });
    
}
