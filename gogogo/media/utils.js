
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

/** Convert a GLatLngBounds object into an array of geohash with 
 * assigned prefix length
 * 
 */

function hashBounds(bounds,prefix_len) {
    var points = [];
    var hashs = new Object();
    var sw = bounds.getSouthWest();
    var ne = bounds.getNorthEast();
    points.push(sw)
    points.push(new GLatLng(ne.lat(),sw.lng())  )
    points.push(ne)
    points.push(new GLatLng(sw.lat(),ne.lng())  )
    
    for (var i =0 ; i < points.length ;i++) {
        var h = encodeGeoHash(points[i].lat() , points[i].lng() );
        hashs[h.substr(0,prefix_len)] = true;
    }
    
    var ret = []
    for (var h in hashs){
        ret.push(h);
    }
    return ret;
}
