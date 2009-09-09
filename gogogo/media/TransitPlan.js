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
    
}

/** Get a summary of the transit plan
 * 
 */

gogogo.TransitPlan.prototype.getSummary = function() {
    var summary = [];
    
    for (var i = 0 ; i < this.transits.length ;i++){
        var transit = this.transits[i];
        if (transit.trip == undefined ){ // Free transfer agency
            summary.push(transit.agency);
        } else {
            summary.push(transit.agency + " " + transit.trip);
        }
    }
    
    return summary.join(",");
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

gogogo.TransitPlan.prototype.createDiv = function(num,modelManager) {
    var id_list = this.getTransitIDList();        
    
    var transit_plan_div = $("<div class='transit_plan' ></div>");    
    var transit_header_div = $("<div></div>");
    var transit_fare_div = $("<div></div>");
    var transit_list_div = $("<div class='transit_list'></div>");
    var transit_op_div = $("<div class='transit_op'></div>");
    
    $(transit_plan_div).append(transit_op_div);
    $(transit_plan_div).append(transit_header_div);
    $(transit_plan_div).append(transit_fare_div);
    $(transit_plan_div).append(transit_list_div);
    
           
    $(transit_header_div).append("<spin>" + num + ". </span>");
    
    $(transit_fare_div).append("$" + this.fare);
    
    $(transit_op_div).append("<a>Detail</a>");
        
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
