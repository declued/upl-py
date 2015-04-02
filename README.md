# UPL Compiler in Python

[![Build Status](http://img.shields.io/travis/declued/upl-py/master.svg)][status]
[![Coverage](http://img.shields.io/coveralls/declued/upl-py/master.svg)][coverage]

Goals of this project are:

* Implement a working compiler for the language which https://github.com/declued/upl wants to implement
* Make the simplest possible decisions
* Avoid over-optimization
* Avoid over-engineering

## Examples

### Calculating absolute value of an integer
```
def abs = (v: int) -> int {
    def result = if(v > 0, v, - v);
    result;
}
```

[status]: https://travis-ci.org/declued/upl-py
[coverage]: https://coveralls.io/r/declued/upl-py
