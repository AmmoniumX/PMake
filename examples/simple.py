from pathlib import Path
import asyncio
from .. import pmake


### Example Usage: basic PMake usage ###


# We have a compile function that takes our target and
#  outputs a list of command arguments
def compile_target(target: pmake.Target) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return ["gcc", *inputs, "-o", str(target.path)]


# We create the Target for our executable "main"
# path: the path for the file that will be produced by this target
# depends: list of paths for the files that this depends on
#  - if missing dependencies have a target, it will compile those first
#  - if they don't have a target, this is an error
# command: function that takes a Target, and returns a list of command arguments
main = pmake.Target(
    path=Path("./main"), depends=[Path("./main.c")], command=compile_target
)

# We register the target, this is needed so we can find how to build missing dependencies
pmake.register_target(main)

# Finally, compile our target. This can compile dependencies asynchronously
# This will also recompile the target if the dependencies are newer than itself
asyncio.run(pmake.compile(main))
