
/** Cluster Manager - Manage cluster on map
 * 
 * @constructor 
 */

gogogo.ClusterManager = function(map,modelManager){
	gogogo.SearchingManager.call(this,map,modelManager);	
	
	// Cluster dictionary
	this.clusters = this.modelManager.cluster_table;
}

extend(gogogo.ClusterManager,gogogo.SearchingManager);

/** Create GOverlay objects
 * 
 * @param items An array of items returned by _search()
 * 
 */

gogogo.ClusterManager.prototype._createOverlays = function(items,callback) {
	var ret = []
	var manager = this;
    
    var total = items.length;
    var count = 0;
    
	$(items).each(function(i,item){		            
		manager.modelManager.queryShape(item.getShape(),function(shape){
            if (!shape.error) {
			var overlay = shape.createOverlay();
			manager.map.addOverlay(overlay);
			ret.push(overlay);
            }
            
            count++;
            if (count == total){
                if (callback!=undefined)
                    callback(ret);
            }
            
		});
	});


}

gogogo.ClusterManager.prototype._search = function(prefix,callback){
	
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter

	var api = "/api/cluster/block?prefix=" + prefix;

	var manager = this;
	
	$.getJSON(api, null , function(data) {
		if (data.stat == "ok") {
		    var list = [];
			$.each(data.data, function(i, item){
				
				if (manager.clusters[item.id] == undefined ) {
                    
                    var cluster = new gogogo.Cluster(item.id);
					cluster.updateFromJson(item,true);
                    
					manager.clusters[item.id] = cluster;
				}
				list.push(manager.clusters[item.id]);
			});
            if (callback){
                callback(list);
            }			
		}
	});

	jQuery.ajaxSettings.cache = cache;		
}
