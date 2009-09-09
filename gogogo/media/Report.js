/** Report - report submission
 *
 * @constructor
 * @base gogogo.Model
 */

gogogo.Report = function(button,link){
    var report = this;
    
    this.link = link;
    
    $(button).click(function(e) {
        report.start();
        e.preventDefault();
    });
}

gogogo.Report.prototype.start = function() {
    var div = $("<div></div>");
    $(div).load(
        this.link,
        function(){
            
            $(div).dialog({ height: 550, width: 700});
            
        });
}
