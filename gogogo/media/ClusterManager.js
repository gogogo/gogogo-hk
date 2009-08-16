
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

gogogo.ClusterManager.prototype.refresh = function(bounds){
	
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter

	var api = "/api/cluster/search/" + 
		bounds.getSouthWest().lat() + "," + bounds.getSouthWest().lng() + "," +
		bounds.getNorthEast().lat() + "," + bounds.getNorthEast().lng();

	var manager = this;
	
	$.getJSON(api, null , function(data) {
		if (data.stat == "ok") {
			$.each(data.data, function(i, item){
				
				if (manager.clusters[item.id] == undefined ) {
					manager.clusters[item.id] = item;
					
					manager.modelManager.queryShape(item.shape,function(shape){
						var overlay = shape.createOverlay();
						manager.map.addOverlay(overlay);
						
					});

				}
			});
		}
	});

	jQuery.ajaxSettings.cache = cache;		
}
