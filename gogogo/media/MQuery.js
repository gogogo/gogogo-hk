
/** MQuery - Query multi-models by using mget in the same time
 * 
 * @constructor 
 */

gogogo.MQuery = function(model){
    this.model = model;
    this.id_list = [];
}

/** Push an ID to the query list
 * 
 */

gogogo.MQuery.prototype.push = function(id){
    this.id_list.push(id);
}

/** Concat an ID list
 * 
 */

gogogo.MQuery.prototype.concat = function(list){
    this.id_list = this.id_list.concat(list);
}

/** Query
 * 
 * @param dict A dictionary of the object table. If the query object is not existed in the table , it will be added automatically.
 * 
 */

gogogo.MQuery.prototype.query = function(dict,callback){
    var mquery = this;
    var ids = [];
    
    var done = function() {
        if (callback) {
            var result = [];
            
            $.each(mquery.id_list,function(i,id){
                result.push(dict[id]);
            });
        
            callback(result);
        }
    }
    
    $.each(this.id_list,function(i,id){
        var object = dict[id];
        if (object==undefined){
            object = new mquery.model(id);
            dict[id] = object;
        }
        
        if (!object.complete && !object.querying){
            ids.push(id);
            object.querying = true;
        }
    });
    
    if (ids.length == 0) {
        done();
    } else {
        var model = new mquery.model();
        
        var api = "/api/" + model.modelType + "/mget?ids=" + ids.join(",");
        var cache = jQuery.ajaxSettings.cache;
        jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
        
        $.getJSON(api, null , function(response) {	
            if (response.stat == "ok"){
                $.each(response.data,function(i,item) {
                    var object = dict[item.id];
                    object.updateFromJson(item,true);                    
                    object.querying = false;
                });
            }
            
            done();
        });
        jQuery.ajaxSettings.cache = cache;	        
        
    }
    
}
