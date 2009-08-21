
/** Replacement of $.extend
 * 
 */

function extend(child, supertype)
{
	// https://developer.mozilla.org/en/Core_JavaScript_1.5_Guide/Inheritance
   // child.prototype.__proto__ = supertype.prototype; 
   // Do not work in IE8
   
   var c = function() {};
    c.prototype = supertype.prototype;
    child.prototype = new c();

}
