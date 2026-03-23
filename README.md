# PMake

A minimal, make-like build system with python.

## Features

- Dependency resolution
- Asynchronous dependency execution
- Staleness checking
- Object oriented `Target` design for custom target metadata

## Usage

Just copy over PMake.py to your project and use it. Please see the `example*.py` files for some examples of how to use PMake. `example-simple.py` makes basic usage of PMake, and `example-custom-target.py` shows how to create a derived Target class for storing custom target metadata.
