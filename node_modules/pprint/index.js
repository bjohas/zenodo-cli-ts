var util = require("util");

// shorthand for console.log
exports.p = console.log.bind(console);

// console.log that deep inspects all arguments via util.inspect
exports.pp = function() {
  var args = [].map.call(arguments,function(x) {
    return util.inspect(x,{depth: null})
  });
  console.log.apply(console,args);
}

// invokes a function on second argument and then returns it,
// useful for debugging pipelines etc, especially with _.partial(tap,snooperFn)
exports.tap = function tap(fn,x) {
  fn(x);
  return x;
}

// pprint.p's an object then returns it
exports.ptap = exports.tap.bind(null,exports.p);

// pprint.pp's an object and returns it
exports.pptap = exports.tap.bind(null,exports.pp);

// pass a snooper fn, returns a function that'll invoke the snooper and return the value
// useful for promises
// 
//   fs.readFileAsync("foo.js")
//     .then(thenp(function snoop(x) { console.log(x.y.z) }))
exports.thenp = function ptap(fn) {
  return function(x) {
    return tap(x,fn);
  }
}

// exposes methods globally (for test/dev convenience only, obvs)
exports.expose = function() {
  ["p","pp","tap","ptap","pptap","thenp"].forEach(function(m) {
    global[m] = exports[m];
  });
}



