/*
 * gogogo.Planner
 * 
 *  Licensed under Affero GPL v3 (www.fsf.org/licensing/licenses/agpl-3.0.html )
 */

/**  Trip Planner
 * 
 * @constructor
 * Custom events:
 * 
 * clarifyAddress(index,address,response)
 * 
 * tripReady(data)
 * 
 */

gogogo.Planner = function(map,output,clusterManager) {
	this.geocoder = new GClientGeocoder();
    
    this.map = map;
    this.clusterManager = clusterManager;
    this.output = output;
	
	/// Array of address point (start , end)
	this.points = [new gogogo.Address(map,"A") , new gogogo.Address(map,"B") ]
	
	this._bindCallback(0);
	this._bindCallback(1);
}

/**
 * Bind the callback to Address object
 */

gogogo.Planner.prototype._bindCallback = function(index){
	var address = this.points[index];
	var planner = this;
	var index = index;

	$(address).bind("clarify",function(event,response) { // Handle clarify event
		$(planner).trigger("clarifyAddress",[index,address,response]);
	});

}

/**
 *  Get address object
 * @param index The index of the address. (0 = start address , 1 = end address)
 */

gogogo.Planner.prototype.getAddress = function(index){
	return this.points[index];
}

/** Clear all the actions that waiting for user's input
 * 
 */

gogogo.Planner.prototype.clearWaitingActions = function() {
    for (var i = 0 ; i < 2; i++){
        this.points[i].clearQueryLocation();
        this.points[i].clearClarifyMarkers();
    }
	
}

/** Query the cluster near to the address.
 * 
 * @param index The index of address
 */

gogogo.Planner.prototype.queryCluster = function (index,callback){
    var address = this.getAddress(index);
    var location = address.getLocation();
        
    var center = hashLatLng(location,gogogo.GEOHASH_PREFIX_LENGTH);
    var top = calculateAdjacent(center,"top");
    var left = calculateAdjacent(center,"left");
    var right = calculateAdjacent(center,"right");
    var bottom = calculateAdjacent(center,"bottom");
    
    var tl = calculateAdjacent(top,"left");
    var tr = calculateAdjacent(top,"right");
    
    var bl = calculateAdjacent(bottom,"left");
    var br = calculateAdjacent(bottom,"right");
    
    var prefix_list = [tl,top ,tr, left,center , right,bl,bottom,br];
    var prefix_recv_count = 0;
    var cluster_list = []

    for (var i = 0 ; i<prefix_list.length ; i++){            
        var prefix = prefix_list[i];
        
        this.clusterManager.search(prefix , function(clusters){
            prefix_recv_count++;
            
            for (var i =0 ; i < clusters.length;i++) {
                var cluster = clusters[i];
                var center = cluster.getCenter();
                if (center.distanceFrom(location) < gogogo.EXPECTED_WALKING_DISTANCE * 1000)
                    cluster_list.push(cluster)
            }
            
            if (prefix_recv_count == 9){
                callback(cluster_list);
            }
        });
    
    }
}

/**
 * Suggest the trip from start to end address
 * @param start  
 */

gogogo.Planner.prototype.suggest = function(start,end,callback) {

	this.points[0].setAddress(start);
	this.points[1].setAddress(end);
	var planner = this;
	
	planner.points[0].queryLocation(function(location){
        
		planner.points[1].queryLocation(function(location) {
            
            planner.queryCluster(0,function(clusters){
                //console.log(clusters);
            });

            
			//@TODO - Implement the real trip planner code
			if (callback != undefined) {
				callback(planner.points[0].getAddress(), planner.points[1].getAddress());	
			}
		});
		
	});


}

