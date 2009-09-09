
/** Model Manager - Manage Model object loading
 * 
 * @constructor 
 */

gogogo.ModelManager = function(){
	
	// Shape dictionary
	this.shape_table = {}
    
    // Agency dictionary
    this.agency_table = {}
    
    this.trip_table = {}
}

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
	object = dict[id];
	
	if (object != undefined) {
		if (object.complete == false) // The information of the object is not completed
			object = undefined;
	}
		
	if (object != undefined) {
		if (callback!=undefined)
			callback(object)
			
		return object;
			
	} else {
		
		if (dict[id] == undefined) {
			dict[id] = new model(id);
		}
		
		object = dict[id];
		object.query(callback);
		
		return undefined;
		
	}
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
