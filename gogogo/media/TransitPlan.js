/** TransitPlan
 * 
 * Transit trip plan. 
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
    
    this.transits = [];
    var plan = this;
    $.each(json.transits,function(i,info){
        var transitInfo =  new gogogo.TransitInfo(info);
        plan.transits.push(transitInfo);
    });
    
    
    /// Array of overlays created by createOverlays
    this.overlays = undefined;
}

/** Process the transit plan
 * 
 */

gogogo.TransitPlan.prototype.process = function( modelManager){
    var plan = this;
    $.each(this.transits,function(i,transit){
       if (transit.trip == undefined )
            plan._processAgency1(transit,modelManager);
    });
}

/** Find parent stations from a stop list
 * 
 */

gogogo.TransitPlan.prototype._findParentStations = function(stop_list,modelManager,callback){
    var parent_table = {}
    var total = stop_list.length;
    var count = 0;
    $.each(stop_list,function(i,stop){
        
        stop.queryParentStation(modelManager,function(parent) {
            if (parent.getID() !=stop.getID())
                parent_table[parent.getID()] = parent;
            count++;
            if (count == total)
                callback(parent_table);
        });
    });
}

/** Process agency with free_transfer service , a pseudo trip will be added 
 * to the transit
 * 
 * */
gogogo.TransitPlan.prototype._processAgency1 = function(transit,modelManager){
    
    var query =[ ["agency" , transit.agency] , ["cluster",transit.on] , ["cluster",transit.off]  ];
    var plan = this;    
    
    modelManager.queryMulti(query,function(result){
        var agency = result[0];
        var cluster_list = [result[1],result[2]]
        var parent_station_list=[];
        var count = 0;
        
        $.each(cluster_list,function(i,cluster){
           cluster.findStopForAgency(agency,modelManager,function(stop_list){
               plan._findParentStations(stop_list , modelManager,function(parent_station_table){
                    parent_station_list[i] = parent_station_table;
                    count ++;
                    if (count == 2) {
                        plan._processAgency2(transit,agency,parent_station_list,modelManager);
                    }
               });
           });
        });
       
    });
}

gogogo.TransitPlan.prototype._processAgency2 = function(transit,agency,parent_station_list,modelManager){
    var total = parent_station_list[0].length * parent_station_list[1].length;
    var count = 0;
    var trip_list = [];
    $.each(parent_station_list[0],function(from_key,from_station){
            $.each(parent_station_list[1],function(to_key,to_station){
                agency.queryPseudoTrip(from_key,to_key,function(){
                    count++;
                    if (count == total){
                        var min = 10000000000;
                        var min_trip;
                        $.each(trip_list,function(i,trip){
                           var stop_id_list= trip_list.getStopIDList();
                           if (stop_id_list.length < min){
                               min = stop_id_list.length
                               min_trip = trip;
                           }
                        });
                        
                        transit.pseudoTrip = min_trip;
                        console.log(min_trip);
                    }                    
                    
                })
                
            });
    });
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

gogogo.TransitPlan.prototype.createDiv = function(num,map,modelManager) {
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
        plan.createOverlays(modelManager,function(overlays){
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

/** Create an array of overlays object to represent the path
 * 
 */

gogogo.TransitPlan.prototype.createOverlays = function(modelManager,callback) {
    if (this.overlays != undefined) {
        callback(this.overlays);
        
        return this.overlays;
    }
    
    this.overlays = [];
    
    var total = this.transits.length;
    var count = 0;
    var plan = this;

    $.each(this.transits,function(i,transit)  {
        transit.createOverlay(modelManager,function(overlay){
            plan.overlays[i] = overlay;
            count++;            
            if (count == total){
                if (callback!=undefined)
                    callback(plan.overlays);
            }
        });
    });
    
}
