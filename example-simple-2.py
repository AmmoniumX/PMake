import asyncio
import PMake
from functools import partial


### Helpers (procedurally generate any target using pure python code) ###
def compile_target(target: PMake.Target, object: bool = False) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    args = [CC, *CFLAGS, *inputs]
    if object:
        args += ["-c"]
    args += ["-o", str(target.path)]
    return args


compile_obj = partial(compile_target, object=True)
compile_exe = partial(compile_target, object=False)

### Recipe ###
CC = "gcc"
CFLAGS = ["-Wall"]


async def clean():
    return await PMake.run_task("rm", "-f", "main", "hello.o")


t_hello = PMake.Target(
    path="example/hello.o", depends=["example/hello.c"], command=compile_obj
)
t_main = PMake.Target(
    path="example/main",
    depends=["example/main.c", "example/hello.o"],
    command=compile_exe,
)


### Execute Recipe ###
async def main():
    # You can do anything before running the recipe, such as modifying globals
    global CC, CFLAGS
    CC = "clang"
    CFLAGS += ["-Wextra", "-O2"]
    # Clean to trigger a full build, just for demonstration
    proc = await clean()
    await proc.wait()
    await PMake.build_target(t_main)


asyncio.run(main())
