import asyncio
import PMake

### Example Usage: basic PMake usage ###

# First we write the "recipe"
CC = "gcc"
CFLAGS = ["-Wall"]


# We have a compile function that takes our target and
#  outputs a list of command arguments
# This is lazily evaluated as a recipe, see why on main()
def compile_target(target: PMake.Target) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return [CC, *CFLAGS, *inputs, "-o", str(target.path)]


async def clean():
    return await PMake.run_task("rm", "-f", "main")


# We create the Target for our executable "main"
# path: the path for the file that will be produced by this target
# depends: list of paths for the files that this depends on
#  - if missing dependencies have a target, it will compile those first
#  - if they don't have a target, this is an error
# command: either a list of command arguments, or a function that takes a Target and returns one
tmain = PMake.Target(
    "main", path="./main", depends=["./main.c"], command=compile_target
)


# Finally, this is the "execute" side. Here we can change whatever we want and have it work
async def main():
    global CC, CFLAGS
    CC = "clang"
    CFLAGS += ["-Wextra", "-O2"]
    # Clean first for example purposes
    proc = await clean()
    await proc.wait()
    await PMake.build_target(tmain)


asyncio.run(main())
