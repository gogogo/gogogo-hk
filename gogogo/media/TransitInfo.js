/** TransitInfo
 * 
 * The detailed information of a transit (e.g. where to pick up and pick off)
 *
 * @constructor 
 */

gogogo.TransitInfo = function (json) {
    this.agency = json.agency;
    this.trip = json.trip;
    this.on = json.on;
    this.off = json.off;
    
    this.overlay = undefined;
}

/** Create overlay for the transit 
 */

gogogo.TransitInfo.prototype.createOverlay = function(modelManager,callback){
    if (this.overlay != undefined){
        
        if (callback!=undefined)
            callback(this.overlay);
            
    }
    var info = this;

    if (this.trip !=undefined) {
                
        modelManager.queryTrip(this.trip,function(trip){
          if (!trip.error){
              trip.queryStops(modelManager,function(){
                  var polyline = trip.createPolyline();
                  info.overlay = polyline;
                
                    if (callback!=undefined){
                        callback(polyline);
                    }
              });
          } else {
              if (callback!=undefined)
                callback();
          }                
        });
        
    } else { // No trip info, create pseudo trip
        this.createPseudoTrip(modelManager, function(trip){

              trip.queryStops(modelManager,function(){
                  var polyline = trip.createPolyline();
                  info.overlay = polyline;
                
                    if (callback!=undefined){
                        callback(polyline);
                    }
              });
        });
    } 
}


/** Find parent stations from a stop list
 * 
 */

gogogo.TransitInfo.prototype._findParentStations = function(stop_list,modelManager,callback){
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
gogogo.TransitInfo.prototype.createPseudoTrip = function(modelManager,callback) {
    var info = this;    
    if (info.pseudoTrip != undefined){
        if (callback!=undefined){
            callback(info.pseudoTrip);
        }
    }
    var query =[ ["agency" , this.agency] , ["cluster",this.on] , ["cluster",this.off]  ];
    
    modelManager.queryMulti(query,function(result){
        var agency = result[0];
        var cluster_list = [result[1],result[2]]
        var parent_station_list=[];
        var count = 0;
        
        $.each(cluster_list,function(i,cluster){
           cluster.findStopForAgency(agency,modelManager,function(stop_list){
               info._findParentStations(stop_list , modelManager,function(parent_station_table){
                    parent_station_list[i] = parent_station_table;
                    count ++;
                    if (count == 2) {
                        info._createPseudoTrip2(agency,parent_station_list,modelManager,callback);
                    }
               });
           });
        });
       
    });    
}

gogogo.TransitInfo.prototype._createPseudoTrip2 = function(agency,parent_station_list,modelManager,callback){
    var info = this;
    var count = 0;
    var trip_list = [];
    var l1=0,l2=0;

    $.each(parent_station_list[0],function(){l1++} )
    $.each(parent_station_list[1],function(){l2++} )
    var total = l1 * l2;
        
    $.each(parent_station_list[0],function(from_key,from_station){
            $.each(parent_station_list[1],function(to_key,to_station){
                agency.queryPseudoTrip(from_key,to_key,function(trip){
                    count++;
                    trip_list.push(trip);
                    
                    if (count == total){
                        var min = 10000000000;
                        var min_trip;
                        $.each(trip_list,function(i,trip){
                           var stop_id_list= trip.getStopIDList();
                           if (stop_id_list.length < min){
                               min = stop_id_list.length
                               min_trip = trip;
                           }
                        });
                        
                        info.pseudoTrip = min_trip;
                        if (callback!=undefined){
                            callback(min_trip);
                        }
                    }                    
                    
                })
                
            });
    });
}
