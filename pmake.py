import asyncio
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Self


@dataclass
class Target:
    path: Path
    depends: list[Path]
    # command may take the same class as Self, including derived subclasses
    command: Callable[[Self], list[str]]


target_builders: dict[Path, Target] = dict()


def register_target(t: Target):
    if t.path in target_builders:
        raise Exception("path already has a target")
    target_builders[t.path] = t
    return t


def is_stale(target: Target) -> bool:
    """Return True if target needs to be rebuilt.

    A target is stale when:
    - it doesn't exist yet, or
    - any dependency is newer than the target itself.
    """
    if not target.path.is_file():
        return True
    target_mtime = target.path.stat().st_mtime
    for dep in target.depends:
        if dep.is_file() and dep.stat().st_mtime > target_mtime:
            return True
    return False


async def compile(target: Target):
    deps = [target_builders[dep] for dep in target.depends if dep in target_builders]
    await asyncio.gather(*[compile(dep) for dep in deps])

    if not is_stale(target):
        print(f"{target.path} is up to date.")
        return

    command = target.command(target)
    print(f"{target.path}:", *command)
    result = await asyncio.create_subprocess_exec(*command)
    await result.wait()
    if result.returncode is None or result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode or -1, target.path)


# Example usage
@dataclass
class CTarget(Target):
    std: str = "c23"


def compile_ctarget(target: CTarget) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return ["gcc", *inputs, f"--std={target.std}", "-o", str(target.path)]


main = CTarget(path=Path("./main"), depends=[Path("./main.c")], command=compile_ctarget)
register_target(main)
asyncio.run(compile(main))
