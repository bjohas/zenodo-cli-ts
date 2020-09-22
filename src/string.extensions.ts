/*
interface String {
    format(): string;
}
*/
// https://www.damirscorner.com/blog/posts/20180216-VariableNumberOfArgumentsInTypescript.html

interface String {
    format(...args: any[]): string;
}

String.prototype.format = function (...args: any[]): string {
  var s = this,
      i = args.length;

  while (i--) {
    //        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    s = s.replace(new RegExp('\\{'+ i + '\\}', 'gm'), arguments[i]);
  }
  return s;
};


