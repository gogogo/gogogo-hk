
/** Cluster
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Cluster = function(id){
	gogogo.Model.call(this,id);
}

extend(gogogo.Cluster,gogogo.Model);

gogogo.Cluster.prototype.modelType = "cluster";

/** Get the shape ID
 * 
 */

gogogo.Cluster.prototype.getShape = function(){
    return this.info.shape;
}

/** Get the center point
 * 
 * @return GLatLng instance
 */

gogogo.Cluster.prototype.getCenter = function(){
    return new GLatLng(this.info.center[0],this.info.center[1] );
}
