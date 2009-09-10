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
}

