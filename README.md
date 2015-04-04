# UPL Compiler

[![Build Status](http://img.shields.io/travis/declued/upl-py/master.svg)][status]
[![Coverage](http://img.shields.io/coveralls/declued/upl-py/master.svg)][coverage]

UPL is a simple, embeddable, strongly typed, functional programming language. Our main goal for creating it was to learn more about compilers and programming languages, while creating something useful.

## Basic Grammar

### Types

UPL provides three basic types:
* bool
* int
* real

UPL currently doesn't support strings, lists, dictionaries, etc. 

### Declarations

* To declare an immutable name, you can use the ```def``` keyword. Attempting to modify the value
  of a immutable name will result in a compile error.

    ```
def a = 1;
    ```

* To declare a mutable name, you can use the ```var``` keyword.

    ```
var a = 1;
    ```

* You can specify the type of a name when declaring it using the ```[var|def] name: type``` syntax.

    ```
var a: int = 1;
    ```
    
* If the type of a name is not specified, it will be inferred from the expression on the right hand side.

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
