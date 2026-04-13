import asyncio
import PMake


### Helpers (proceturally generate any target using pure python code) ###
def compile_target(target: PMake.Target) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return [CC, *CFLAGS, *inputs, "-o", str(target.path)]


### Recipe ###
CC = "gcc"
CFLAGS = ["-Wall"]


async def clean():
    return await PMake.run_task("rm", "-f", "main")


tmain = PMake.Target(path="./main", depends=["./main.c"], command=compile_target)


### Execute Recipe ###
async def main():
    # You can do anything before running the recipe, such as modifying globals
    global CC, CFLAGS
    CC = "clang"
    CFLAGS += ["-Wextra", "-O2"]
    proc = await clean()
    await proc.wait()
    await PMake.build_target(tmain)


asyncio.run(main())
