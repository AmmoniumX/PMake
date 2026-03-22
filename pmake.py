import asyncio
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Callable


@dataclass
class Target:
    path: Path
    depends: list[Path]
    command: Callable[[Target], list[str]]


target_builders: dict[Path, Target] = dict()


def target(path: Path, depends: list[Path], command: Callable[[Target], list[str]]):
    t = Target(path, depends, command)
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


def compile_cmd(target: Target) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return ["gcc", *inputs, "-o", str(target.path)]


# Example usage
main = target(path=Path("./main"), depends=[Path("./main.c")], command=compile_cmd)
asyncio.run(compile(main))
