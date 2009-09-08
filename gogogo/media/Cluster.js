
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

gogogo.Cluster.prototype.getShape = function(){
    return this.info.shape;
}
