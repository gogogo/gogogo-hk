
/** Model Manager - Manage Model object loading
 * 
 * @constructor 
 */

gogogo.ModelManager = function(){
	
	// Shape dictionary
	this.shape_table = {};
    
    // Agency dictionary
    this.agency_table = {};
    
    this.trip_table = {};
    
    this.stop_table = {};
    
    this.cluster_table = {};
}

/** A global model manager for all page
 * 
 */

gogogo.modelManager = new gogogo.ModelManager();

/** Query an object with a type from server(internal function)
 * 
 * @param model The constructor function of the object type.
 * 
 * @param dict A dictionary that store all the queryed objects
 * 
 * @param id The ID of the object
 * 
 * @param callback The callback function 
 */

gogogo.ModelManager.prototype._query = function(model,dict,id,callback){
	var object = dict[id];
	
	if (object == undefined) {
        object = new model(id);
        dict[id] = object;
	}
        
	if (object.complete) {
        
		if (callback!=undefined)
			callback(object)
			
		return object;
			
	} else {
		
		object.query(callback);
		
	}
}

/** Query multi-models by using mget in the same time
 * 
 */

gogogo.ModelManager.prototype._queryList = function(model,dict,ids,callback){
    mquery = new gogogo.MQuery(model);
    mquery.concat(ids);
    mquery.query(dict,callback);    
}

/** Query multiple items at a time
 * 
 */

gogogo.ModelManager.prototype.queryMulti = function(list,callback){
    var total = list.length;
    var result = [];
    var count = 0;
    var manager = this;
    
    var op_table = {    
        agency : [gogogo.Agency,this.agency_table],
        shape : [gogogo.Shape,this.shape_table],
        stop : [gogogo.Stop,this.stop_table],
        trip : [gogogo.Trip,this.trip_table],
        cluster : [gogogo.Cluster,this.cluster_table],
    };
    
    $.each(list,function(i,query){
        var model = query[0];
        var id = query[1];
        var op = op_table[model];
        manager._query(op[0],op[1],id,function(obj){
            result[i] = obj;
            count++;
            if (count ==total){
                if (callback!=undefined){
                    callback(result);
                }
            }
        });
    });
}

/** Query ageny information from server
 * 
 */

gogogo.ModelManager.prototype.queryAgency = function(id,callback) {
    
	return this._query(gogogo.Agency,this.agency_table,id,callback)
}

/** Query shape from server
 * 
 */

gogogo.ModelManager.prototype.queryShape = function(id,callback) {
	return this._query(gogogo.Shape,this.shape_table,id,callback)
}

/** Query trip information from server
 * 
 */

gogogo.ModelManager.prototype.queryTrip = function(id,callback) {
    
	return this._query(gogogo.Trip,this.trip_table,id,callback)
}

/** Query multiple trip information from server
 * 
 */

gogogo.ModelManager.prototype.queryTripList = function(ids,callback) {
	return this._queryList(gogogo.Trip,this.trip_table,ids,callback);
}

/** Query stop information from server
 * 
 */

gogogo.ModelManager.prototype.queryStop = function(id,callback) {
    
	return this._query(gogogo.Stop,this.stop_table,id,callback)
}

/** Query multiple stop information from server
 * 
 */

gogogo.ModelManager.prototype.queryStopList = function(ids,callback) {
	return this._queryList(gogogo.Stop,this.stop_table,ids,callback);
}
