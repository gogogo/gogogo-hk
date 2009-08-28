
/** Cluster Manager - Manage cluster on map
 * 
 * @constructor 
 */

gogogo.ClusterManager = function(map,modelManager){
	gogogo.SearchingManager.call(this,map);	
	
	// Cluster dictionary
	this.clusters = Object();
	this.modelManager = modelManager;
}

extend(gogogo.ClusterManager,gogogo.SearchingManager);

/** Create GOverlay objects
 * 
 * @param items An array of items returned by _search()
 * 
 */

gogogo.ClusterManager.prototype._createOverlays = function(items) {
	var ret = []
	var manager = this;
	$(items).each(function(i,item){		
		manager.modelManager.queryShape(item.shape,function(shape){
			var overlay = shape.createOverlay();
			manager.map.addOverlay(overlay);
			ret.push(overlay);
		});
	});
	
	return ret;
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
					manager.clusters[item.id] = item;
					
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
