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
 * error(message)
 * 
 */

gogogo.Planner = function(map,output,clusterManager) {
	this.geocoder = new GClientGeocoder();
    
    this.map = map;
    this.clusterManager = clusterManager;
    this.output = output;
	
	/// Array of address point (start , end)
	this.points = [new gogogo.Address(map,"A") , new gogogo.Address(map,"B") ]
	
    /// Storage of TransitPlan instance
    this.plan_list = []
    
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
 * Signals :
 * 
 * noClusterFound - Emitted if no any cluster found
 *  
 * @param index The index of address
 * @param callback Called if any cluster was found near to the address
 *
 */

gogogo.Planner.prototype.queryCluster = function (index,callback){
    var planner = this;
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
                if (cluster_list.length > 0) {
                    callback(cluster_list);
                } else {
                    $(planner).trigger("noClusterFound",address);                    
                }
            }
        });
    
    }
}

/** Prepare required information for trip planning
 */

gogogo.Planner.prototype._prepare = function(modelManager,callback) {

	var planner = this;
    var start_clusters = [];
    var goal_clusters = [];

	planner.points[0].queryLocation(function(location){
		planner.points[1].queryLocation(function(location) {            
            planner.queryCluster(0,function(clusters) {
                start_clusters = clusters;
                planner.queryCluster(1,function(clusters) {
                    goal_clusters = clusters;
                    planner._plan(start_clusters,goal_clusters,modelManager,callback);
                });
            });
                    
		});
		
	});
}

/** Query the "plan" from start clusters to goal_cluster
 * 
 */

gogogo.Planner.prototype._plan = function (start_clusters, goal_clusters ,modelManager,callback){
    var total = start_clusters.length * goal_clusters.length;
    
    var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
    
    var plan = []
    var count = 0;

    var planner = this;

    planner.plan_list = []
    
    for (var i = 0 ; i< start_clusters.length; i++) {
        for (var j = 0 ; j < goal_clusters.length; j++) {
            api = "/api/plan?from=" + start_clusters[i].getID()  + "&to=" + goal_clusters[i].getID();
            $.getJSON(api, null , function(response) {	
                
                if (response.stat == "ok") {
                    var plans = response.data.plans;
                    
                    for (var k = 0 ; k < plans.length;k++) {
                        var json = plans[k];
                        var plan = new gogogo.TransitPlan(json);
                        plan.process(modelManager);
                        planner.plan_list.push(plan);
                    }
                }

                count ++;
                if (count == total){
                    if (callback != undefined) {
                        callback();	
                    }
                                    
                }

            });

        }
    }
    jQuery.ajaxSettings.cache = cache;	
}

/**
 * Suggest the trip from start to end address
 * @param start  
 */

gogogo.Planner.prototype.suggest = function(start,end,modelManager,callback) {
	this.points[0].setAddress(start);
	this.points[1].setAddress(end);
	
    this._prepare(modelManager,callback);

}

gogogo.Planner.prototype.getTransitPlanList = function(){
    return this.plan_list;
}

