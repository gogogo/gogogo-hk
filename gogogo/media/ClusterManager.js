
/** Cluster Manager - Manage cluster on map
 * 
 * @constructor 
 */

gogogo.ClusterManager = function(map){
	gogogo.SearchingManager.call(this,map);	
	
	// Cluster dictionary
	this.clusters = Object();
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
					
					manager.clusters[item.id];
				}
			});
		}
	});

	jQuery.ajaxSettings.cache = cache;		
}
