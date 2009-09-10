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
        if (callback!=undefined)
            callback();
    } 
}
