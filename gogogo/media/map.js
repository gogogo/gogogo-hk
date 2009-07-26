/*
 * gogogo.Map
 *
 *  Licensed under Affero GPL v3 (www.fsf.org/licensing/licenses/agpl-3.0.html )
 */

gogogo.Map = function (container){
	GMap2.call(this,container);
	this.setUIToDefault();
	
	this.setCenter(new GLatLng(gogogo.DEFAULT_LOCATION[0],gogogo.DEFAULT_LOCATION[1])
		, gogogo.DEFAULT_ZOOM);
};

$.extend(gogogo.Map,GMap2);
