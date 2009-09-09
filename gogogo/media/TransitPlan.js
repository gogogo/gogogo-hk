/** TransitPlan
 * 
 * Transit trip planning
 *
 * @constructor 
 */

gogogo.TransitPlan = function (json) {
    this.fare = json.fare;
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
