import asyncio
import PMake

### Example Usage: basic PMake usage ###
CC = "gcc"
CFLAGS = ["-Wall", "-Wextra", "-Werror", "-O2"]


# We have a compile function that takes our target and
#  outputs a list of command arguments
def compile_target(target: PMake.Target) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return [CC, *CFLAGS, *inputs, "-o", str(target.path)]


# We create the Target for our executable "main"
# path: the path for the file that will be produced by this target
# depends: list of paths for the files that this depends on
#  - if missing dependencies have a target, it will compile those first
#  - if they don't have a target, this is an error
# command: either a list of command arguments, or a function that takes a Target and returns one
main = PMake.Target(path="./main", depends=["./main.c"], command=compile_target)

# Finally, compile our target. This can compile dependencies asynchronously
# This will also recompile the target if the dependencies are newer than itself
asyncio.run(PMake.build_target(main))
