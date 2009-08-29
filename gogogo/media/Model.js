
/** Model class 
 * 
 * Based class of all model object from gogogo server.
 * 
 * @constructor 
 * 
 * Signals:
 * 
 * 	complete - The query is completed.
 */

gogogo.Model = function(id){

	// The object contains complete information of the model object
	this.complete = false
	
	// TRUE if it is querying the complete information of the model object from server
	this.querying = false;
    
    // TRUE if there has any error in fetching the data
    this.error = false;
	
	/// Store the detailed information of the model.
	this.info = Object(); 
	
	// The ID of the model
	this.id = id;
}

/**
 * Update from JSON
 */
gogogo.Model.prototype.updateFromJson = function(json){
	var trip = this;
	
	for (attr in json){
		this.info[attr] = json[attr];
	}
	
}

/**
 * Query the complete information from server
 * 
 * @param callback The callback function to be involved after the operation. The first arg is model instance , the second arg is the response from server
 * 
 */

gogogo.Model.prototype.query = function(callback) {
	var	model = this;
		
	if (this.querying) {
		if (callback!=undefined){
			$(this).one("query-finished" , function(e,response){
				callback(model,response);
			});
		}
		return;
	}
	
	this.querying = true;
	
	api = "/api/" + this.modelType + "/get?id=" + this.id;
	var cache = jQuery.ajaxSettings.cache;
	jQuery.ajaxSettings.cache = true; // Prevent the "_" parameter
	
	$.getJSON(api, null , function(response) {	
		if (response.stat == "ok"){
			model.error = false;
			model.updateFromJson(response.data);
			model.complete = true;
		} else {
            model.error = true;
            model.complete = false;
        }
        
        $(model).trigger("query-finished",response);        
		
		if (callback!=undefined)
			callback(model,response);
		
		model.querying = false;
	});
	jQuery.ajaxSettings.cache = cache;	
}

