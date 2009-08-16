
/** Shape
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Shape = function(id){
	gogogo.Model.call(this,id);
	this.overlay = undefined;
}

extend(gogogo.Shape,gogogo.Model);

gogogo.Shape.prototype.modelType = "shape";

/** Create GMap overlay object
 *
 */ 

gogogo.Shape.prototype.createOverlay = function(options){
	
	if (this.overlay != undefined)
		return this.overlay;
		
	var j = 0;
	var pts = [];
	
	for (var i = 0 ; i < this.info.points.length ;i+=2,j++) {
		pts[j] = new GLatLng(this.info.points[i],this.info.points[i+1]);
	}
	
	if (this.info.type == 0 ){
		this.overlay = new GPolyline(pts,this.info.color,5,0.4,options);		
	} else {
		this.overlay = new GPolygon(pts,this.info.color,5,0.4,this.info.color,0.3 ,options);
	}

	
	return this.overlay;
}
