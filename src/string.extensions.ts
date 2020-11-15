/*
interface String {
    format(): string;
}
*/
// https://www.damirscorner.com/blog/posts/20180216-VariableNumberOfArgumentsInTypescript.html

interface String {
    formatN(...args: any[]): string;
    format(...args: any[]): string;
  }

String.prototype.formatN = function (...args: any[]): string {
  var s = this,
      i = args.length;

  while (i--) {
    //        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    s = s.replace(new RegExp('\\{'+ i + '\\}', 'gm'), arguments[i]);
  }
  return s;
};


String.prototype.format = function (): string {
    var result = arguments[0];
    for (var i = 0; i < arguments.length - 1; i++) {
        var reg = new RegExp("\\{" + i + "\\}", "gm");
        result = result.replace(reg, arguments[i + 1]);
    }
    return result;
}

