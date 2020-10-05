/*
interface String {
    format(): string;
}
*/
// https://www.damirscorner.com/blog/posts/20180216-VariableNumberOfArgumentsInTypescript.html
String.prototype.format = function () {
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
    }
    var s = this, i = args.length;
    while (i--) {
        //        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};
