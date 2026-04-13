import asyncio
import PMake
from dataclasses import dataclass

### Example Usage: Custom Target derived class ###


# We create a custom target class derived form Target
#  This is optional, useful for storing extra metadata
#  for your target such as `std`
@dataclass
class CTarget(PMake.Target):
    std: str = "c23"


# We have a compile function that takes our target (here, CTarget) and
#  outputs a list of command arguments
def compile_ctarget(target: CTarget) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return ["gcc", *inputs, f"--std={target.std}", "-o", str(target.path)]


# We create the Target for our executable "main"
# path: the path for the file that will be produced by this target
# depends: list of paths for the files that this depends on
#  - if missing dependencies have a target, it will compile those first
#  - if they don't have a target, this is an error
# command: function that takes a self argument (Target or derived class like CTarget),
#  and returns a list of command arguments
main = CTarget("main", path="./main", depends=["./main.c"], command=compile_ctarget)

# Finally, compile our target. This can compile dependencies asynchronously
asyncio.run(PMake.build_target(main))
