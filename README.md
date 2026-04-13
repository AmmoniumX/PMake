# PMake

A minimal, make-like build system with python.

## Features

- Dependency resolution
- Asynchronous dependency execution
- Staleness checking
- Object oriented `Target` design for custom target metadata

## Usage

Just copy over PMake.py to your project and use it.

PMake can be called directly or imported, see example usages:

```
$ ./PMake.py --target clean && ./PMake.py
Loaded targets: hello, main, clean (explicit)
clean: rm -f example/main example/hello.o
Loaded targets: hello, main, clean (explicit)
example/hello.o: gcc -Wall example/hello.c -c -o example/hello.o
example/hello.c: In function ‘say_hello’:
example/hello.c:4:7: warning: unused variable ‘x’ [-Wunused-variable]
    4 |   int x = 1; // unused variable (compiler output is passed through)
      |       ^
example/main: gcc -Wall example/main.c example/hello.o -o example/main

$ python example-simple-2.py 
rm -f example/main example/hello.o
example/hello.o: clang -Wall -Wextra -O2 example/hello.c -c -o example/hello.o
example/hello.c:4:7: warning: unused variable 'x' [-Wunused-variable]
    4 |   int x = 1; // unused variable (compiler output is passed through)
      |       ^
1 warning generated.
example/main: clang -Wall -Wextra -O2 example/main.c example/hello.o -o example/main
```
