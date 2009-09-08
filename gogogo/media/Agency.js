/** Agency
 * 
 * @constructor 
 * @extends gogogo.Model
 
 */

gogogo.Agency = function(id){
	gogogo.Model.call(this,id);
}

extend(gogogo.Agency,gogogo.Model);

gogogo.Agency.prototype.modelType = "agency";

gogogo.Agency.prototype.getName = function() {
    return this.info.name;
}
