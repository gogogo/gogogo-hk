
/** Model Manager - Manage Model object loading
 * 
 * @constructor 
 */

gogogo.ModelManager = function(){
	
	// Shape dictionary
	this.shapes = Object();
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

gogogo.ModelManager.prototype.queryShape = function(id,callback) {
	return this._query(gogogo.Shape,this.shapes,id,callback)
}
