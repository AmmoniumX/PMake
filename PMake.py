import asyncio
import subprocess
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Self, cast

type StrPath = str | os.PathLike[str]

target_builders: dict[Path, Target] = dict()


def register_target(t: Target):
    path = cast(Path, t.path)  # We know its Path from postinit
    if t.path in target_builders:
        raise Exception(f"There is already a target for the path {t.path}")
    target_builders[path] = t

    return t


@dataclass()
class Target:
    path: StrPath
    depends: list[StrPath]
    # command may take the same class as Self, including derived subclasses
    command: Callable[[Self], list[str]] | list[str]
    auto_register: bool = field(default=True, repr=False)

    def __post_init__(self):
        self.path = Path(self.path)
        self.depends = [Path(dep) for dep in self.depends]

        if self.auto_register:
            register_target(self)

    def get_command(self) -> list[str]:
        if callable(self.command):
            return self.command(self)
        return self.command


def is_stale(target: Target) -> bool:
    """Return True if target needs to be rebuilt.

    A target is stale when:
    - it doesn't exist yet, or
    - any dependency is newer than the target itself.
    """

    # Inform the type checker we know path and deps are Path from postinit
    path = cast(Path, target.path)
    deps = cast(list[Path], target.depends)

    if not path.is_file():
        return True
    target_mtime = path.stat().st_mtime

    for dep in deps:
        if dep.is_file() and dep.stat().st_mtime > target_mtime:
            return True
    return False


async def build_target(target: Target):
    deps = [target_builders[dep] for dep in target.depends if dep in target_builders]
    await asyncio.gather(*[build_target(dep) for dep in deps])

    if not is_stale(target):
        print(f"{target.path} is up to date.")
        return

    command = target.get_command()
    print(f"{target.path}:", *command)
    result = await asyncio.create_subprocess_exec(*command)
    await result.wait()
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode or -1, target.path)
