
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

gogogo.Cluster.prototype.findStopForAgency = function(agency,stopManager,callback) {
    var total = this.info.members.length;
    var count = 0;
    var stop_list = []
    
    $.each(this.info.members,function(i,member) {
        stopManager.queryStop(member,function(stop){
            if (stop.getAgencyID() == agency.getID()) {
                stop_list.push(stop);
            }
            
            count++;
            if (count == total){
                if (callback!=undefined)           
                    callback(stop_list);
            }
        });
        
    });
}

