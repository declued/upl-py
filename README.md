# UPL Compiler

[![Build Status](http://img.shields.io/travis/declued/upl-py/master.svg)][status]
[![Coverage](http://img.shields.io/coveralls/declued/upl-py/master.svg)][coverage]

UPL is a simple, embeddable, strongly typed, functional programming language. Our main goal for creating it was to learn more about compilers and programming languages, while creating something useful.

## Installation and Running the Tests

First, you need the following:
* [Python 2.7, 3.2, 3.3, or 3.4][python]
* [pip][pip]

Then, to install the required packages run:

```
sudo pip install -r requirements.txt
```

Now, you can run tests using the following command:

```
./run_tests.sh
```

## Basic Grammar

### Types
UPL provides three basic types:
* bool
* int
* real

UPL currently doesn't support strings, lists, dictionaries, etc. 

### Statements
A statement is a declaration or an expression. A program consists of a sequence of statements.


### Declarations
* To declare an immutable name, you can use the ```def``` keyword. Attempting to modify the value
  of a immutable name will result in a compile error.

    ```
def a = expression;
    ```

* To declare a mutable name, you can use the ```var``` keyword.

    ```
var a = expression;
    ```

* You can specify the type of a name when declaring it using the ```{var|def} name: type``` syntax.

    ```
var a: int = expression;
    ```
    
* If the type of a name is not specified, it will be inferred from the expression on the right hand side.

### Expressions
* A expression can be formed in one of the following ways:

  ```
expression := literal | 
                  identifier |
                  expression operator expression |      # binary operation
                  operator expression |                 # unary operaiton
                  function_name(arg_1, ..., arg_n) |    # function call
                  function_definition |
                  "(" expression ")"                    # nested exprssion
  ```

* An int literal consists of a sequence of digits.
* A real literal has the form of: ```int_lit “.” int_lit [“e” [“+”|“-”] int_lit]```.
* A bool literal is either ```true``` or ```false```.
* An operator is a non-empty sequence of the characters in the ```~!@$%^&*-+/=<>|``` set.
* Operator priorities are:

  ```
||  ^^  &&
|   ^   &
==  !=
<   <=  >=  >
<<  >>  <<> >><
+   -
*   /   %
**
Other operators
  ```

### Functions
* To define a function, you can use the following syntax:

  ```
{var|def} func_name = (arg_1: type_1, ..., arg_n: type_2) -> return_type 
{
       statement_1;
       ...
       statement_m;
}
  ```

* Return value of a function is the result of evaluation of its last statement.
* Functions can be nested.

## Examples

### Calculating absolute value of an integer
```
def abs = (v: int) -> int {
    def result = if(v > 0, v, -v);
    result;
}
```

### Fibonacci Sequence
```
def fib = (n: int) -> int {
    if(n <= 1, 1, fib(n - 1) + fib(n - 2));
}
```

[status]: https://travis-ci.org/declued/upl-py
[coverage]: https://coveralls.io/r/declued/upl-py
[python]: https://www.python.org/
[pip]: https://pypi.python.org/pypi/pip
