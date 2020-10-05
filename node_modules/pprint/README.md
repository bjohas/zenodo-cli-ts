# pprint

Printing/logging helpers for testing/development.

```javascript
pprint.p // shorthand for console.log

pprint.pp // console.log that deep inspects all arguments via util.inspect

// invokes a function on second argument and then returns it,
// useful for debugging pipelines etc, especially with _.partial(tap,snooperFn)
pprint.tap 

// pprint.p's an object then returns it
pprint.ptap

// pprint.pp's an object and returns it
pprint.pptap

// exposes methods globally (for test/dev environments only, obviously)
pprint.expose
```

## Promises

```
// pass a snooper fn, returns a function that'll invoke the snooper and return the value
// useful for promises
pprint.thenp

// e.g
readPromise("foo.js")
  .then(
    thenp(function snoop(x) { console.log(x.y.z) })
  )
````






