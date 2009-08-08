
/** Replacement of $.extend
 * https://developer.mozilla.org/en/Core_JavaScript_1.5_Guide/Inheritance
 */

function extend(child, supertype)
{
   child.prototype.__proto__ = supertype.prototype;
}
