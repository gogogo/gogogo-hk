
/** Replacement of $.extend
 * 
 */

function extend(child, supertype)
{
	// https://developer.mozilla.org/en/Core_JavaScript_1.5_Guide/Inheritance
   // child.prototype.__proto__ = supertype.prototype; 
   // Do not work in IE8
   
   var c = function() {};
    c.prototype = supertype.prototype;
    child.prototype = new c();

}

/** Create geohash on a given point and prefix length
 * 
 */

function hashLatLng(pt , prefix_len) {
    var hash = encodeGeoHash(pt.lat() , pt.lng() );
    return hash.substr(0,prefix_len);
}

/** Convert a GLatLngBounds object into an array of geohash with 
 * assigned prefix length
 * 
 */

function hashBounds(bounds,prefix_len) {    
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
        
    var hashSW = hashLatLng(sw,prefix_len);
    //var hashNE = encodeGeoHash(ne.lat() , ne.lng() )
    var hashNW = hashLatLng(new GLatLng(ne.lat() , sw.lng() ) , prefix_len);
    var hashSE = hashLatLng(new GLatLng(sw.lat() , ne.lng() ) , prefix_len);
    var ret = [];
    
    var x = 1;
    var y = 1;
    var hash0 = hashSW;
        
    while (hash0 != hashNW) {
        y++;
        hash0 = calculateAdjacent(hash0 , "top");
    }   
        
    hash0 = hashSW;
    while (hash0 != hashSE){
        x++;
        hash0 = calculateAdjacent(hash0 , "right");
    }
    
    hash0 = hashSW;
    for (var i = 0 ; i < y;i++){
        var hash1 = hash0
        for (var j = 0 ; j < x ;j++) {
            ret.push(hash1);
            hash1 = calculateAdjacent(hash1 , "right");
        }
        
        hash0 = calculateAdjacent(hash0 , "top");
    }
    
    return ret;
}
