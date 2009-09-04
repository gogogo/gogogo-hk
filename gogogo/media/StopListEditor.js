
/** Stop List Editor
 * 
 * A widget to edit stop list
 * 
 * @param map A GMap2 instance
 * 
 * @constructor 
 */

gogogo.StopListEditor = function (map,input,sortable){
    this.map = map;
    
    this.input = input;
    
    this.sortable = sortable;
    
    this.stopManager = new gogogo.StopManager(map);
    
    this.trip = new gogogo.Trip();    
    
    var editor = this;
    
    $(this.stopManager).bind("markerAdded",function (e,marker,stop) {
        GEvent.addListener(marker, "mousedown", function(){
            editor.addStopID(stop.getID());
        });
    });
    
};

/** Initialize the editor
 * 
 */

gogogo.StopListEditor.prototype.init = function(){
    this.sortable.sortable();
    var editor = this;
    
    this.sortable.bind("sortstop",function (e,ui){
        editor._onSortableChanged();
    });            
    

    this._updateSortable();
    this._updateOverlay(false);
    
    this.input.change(function(){
        editor._updateSortable();
        editor._updateOverlay(false);        
    });
    
}

/** Add Stop ID
 */

gogogo.StopListEditor.prototype.addStopID = function(id){
    var value = this.input.val();
    var items = value.split(",")
    items.push(id);
    this.input.val(items.join(","));

    this._updateSortable();
    this._updateOverlay(true);
}

gogogo.StopListEditor.prototype._createDeleteLink = function(parent) {
    var editor = this;
    var a = $("<a>[X]</a> ");
    a.click(function (){
       $(parent).remove();
       editor._onSortableChanged();
    });
    return a;
}


/** Called when the sortable object is changed
 */
gogogo.StopListEditor.prototype._onSortableChanged = function() {
   this.input.val(this.sortable.sortable('toArray'));
   
   this._updateOverlay(false);     
}

gogogo.StopListEditor.prototype._updateSortable = function(){
    var value = this.input.val();
    var keys = value.split(",");
    this.sortable.empty();
    for (var i = 0 ; i < keys.length;i++){
        
        var li = $("<li></li>");
        var a = this._createDeleteLink($(li));
        
        $(li).attr("id",keys[i]);
        $(li).append(a);
        $(li).append(keys[i]);
        
        this.sortable.append(li);
    }
    this.sortable.sortable("refresh");
}

gogogo.StopListEditor.prototype._updateOverlay = function(nozoom){
    var value = this.input.val();
    var keys = value.split(",");
    
    var polyline = this.trip.getPolyline();
    if (polyline) {
        this.map.removeOverlay(polyline);
    }
    this.trip.removePolyline();

    this.trip.setStopIDList(keys);
    
    var editor = this;
                    
    this.trip.queryStops(this.stopManager , function(trip){
        var line = editor.trip.createPolyline();
        editor.map.addOverlay(line);
        
        if (!nozoom)
            trip.zoomAndPan(editor.map);
        var kids = editor.sortable.children();
        
        $.each(kids,function(i,child){
            var stop_list = editor.trip.getStopList();
            var id = $(child).attr("id");
            
            for (var i = 0 ; i< stop_list.length;i++) {
                var stop  = stop_list[i];
                if (stop.getID() == id) {
                    if (!stop.error) {
                        var a = editor._createDeleteLink(child);
                        
                        $(child).empty();
                        $(child).append(a);
                        $(child).append(stop.getName());
                    } else {
                        $(child).addClass("error");
                    }
                    break;
                }
            }
            
        });
    });    
}
