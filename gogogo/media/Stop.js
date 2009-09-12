
/** Stop
 *
 * @constructor
 * @base gogogo.Model
 */

gogogo.Stop = function(id){
    gogogo.Model.call(this,id);

    this.marker = undefined;
    
    /// Reference of agency model
    this.agency = undefined;
}

extend(gogogo.Stop , gogogo.Model)

//$.extend(gogogo.Stop , gogogo.Model) // Can not be used  updateFromJson() will raise "too much recursion"

gogogo.Stop.prototype.modelType = "stop";

/**
 * Update from JSON
 */

gogogo.Stop.prototype.updateFromJson = function(json,complete){

    gogogo.Model.prototype.updateFromJson.call(this,json,complete);

    if (json.latlng != undefined) {
        this.latlng = new GLatLng(json.latlng[0], json.latlng[1]);
    }
}

/**
 * Create marker overlay. If it is already created, it will return the created marker.
 */

gogogo.Stop.prototype.createMarker = function(){
    if (this.marker == undefined) {
        var option = {
            "title": this.info.name
        };

        agency = this.queryAgency();        
       
        if (agency){
            var icon = agency.createTranitIcon();
            if (icon!=undefined)
                option["icon"] = icon;
        }
        
        this.marker = new GMarker(this.latlng,option);
    }

    return this.marker;
}

/** Return a GLatLng instance of the location of the stop
 * 
 */

gogogo.Stop.prototype.getLatLng  = function(){
    return this.latlng;
}

/** Get the name of the stop
 * 
 */

gogogo.Stop.prototype.getName = function(){
    return this.info.name;
}

gogogo.Stop.prototype.getAgencyID = function (){
    return this.info.agency;
}

gogogo.Stop.prototype.getType = function(){
    return this.info.type;
}

/** Query the parent station. If no parent station is existed, it will
 * return the stop itself.
 * 
 * @param manager Either of StopManager and ModelManager is accepted
 * 
 */

gogogo.Stop.prototype.queryParentStation = function(manager,callback){
    if (this.parent_station != undefined){
        return this.parent_station;
    }
    
    var stop = this;
    
    if (this.info.parent_station == undefined){
        this.parent_station = this;
        if (callback!=undefined)
            callback(this.parent_station);
    } else {
        manager.queryStop(this.info.parent_station,function(parent_station){
            stop.parent_station = parent_station;
            if (callback!=undefined)
                callback(stop.parent_station);
        });
    }
    
    return stop.parent_station;
}


/** Query the parent agency
 * 
 */

gogogo.Stop.prototype.queryAgency = function(callback){
    if (this.agency!=undefined){
        if (callback!=undefined)
            callback(this.agency);

        return this.agency;
    }
    
    var stop = this;
    
    if (this.info.agency == undefined){
        if (callback!=undefined)
            callback();
    } else {
        gogogo.modelManager.queryAgency(this.info.agency,function(agency){
             stop.agency = agency;
             
             if (callback!= undefined){
                 callback(agency);
             }   
        });
    }
    
    return this.agency;
}
