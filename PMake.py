#!/usr/bin/env python

import asyncio
import subprocess
import argparse

from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Self, TypeVar

_all_targets: dict[str, Target] = dict()
_implicit_targets: list[Target] = list()
_target_builders: dict[str, Target] = dict()
_build_tasks: dict[str, asyncio.Task] = dict()


def require[T](value: T | None, msg: str = "Required value is None") -> T:
    if value is not None:
        return value
    raise ValueError(msg)


def register_target(t: Target):
    if t.name in _all_targets:
        raise Exception(f"There is already a target for the name {t.name}")
    _all_targets[t.name] = t
    if not t.explicit:
        _implicit_targets.append(t)
    if t.path is not None:
        _target_builders[t.path] = t


@dataclass()
class Target:
    name: str
    path: str | None
    depends: list[str]
    type Command = list[str] | str
    type CommandProperty = Callable[[Self], Command] | Command
    # command may take the same class as Self, including derived subclasses
    command: CommandProperty
    predicate: Callable[[Self], bool] | bool | None = field(default=None)

    auto_register: bool = field(default=True, repr=False)
    explicit: bool = field(default=False)

    def __post_init__(self):
        if self.auto_register:
            register_target(self)

    def get_command(self) -> list[str]:
        if callable(self.command):
            return parse_command(self.command(self))
        return parse_command(self.command)

    def get_predicate(self) -> bool:
        predicate = require(
            self.predicate, "predicate cannot be None when called in get_predicate"
        )
        if callable(predicate):
            return predicate(self)
        return predicate


def parse_command(c: Target.Command | tuple[str, ...]) -> list[str]:
    if isinstance(c, str):
        return c.split()
    if isinstance(c, (list, tuple)) and len(c) == 1 and isinstance(c[0], str):
        return c[0].split()
    return list(c)


# "Alias" for a Target that is explicit, has no depends, and will always be called
def Task(
    name: str,
    command: Target.CommandProperty,
):
    return Target(
        name, path=None, depends=[], command=command, predicate=True, explicit=True
    )


def must_build(target: Target) -> bool:
    """Return True if target needs to be rebuilt.

    A target is stale when:
    - it contains a custom predicate which evaluates to True
    - it doesn't exist yet, or
    - any dependency is newer than the target itself.
    """

    if target.path is None:
        if target.predicate is not None:
            return target.get_predicate()
        else:
            raise RuntimeError(
                f"Targets without path must contain a predicate: {target.name}"
            )

    path = Path(target.path)
    deps = [Path(d) for d in target.depends]

    if not path.is_file():
        return True
    target_mtime = path.stat().st_mtime

    for dep in deps:
        if dep.is_file() and dep.stat().st_mtime > target_mtime:
            return True
    return False


async def run_task(*args: str, silent: bool = False):
    command = parse_command(args)
    if not silent:
        print("Running task", *command)
    return await asyncio.create_subprocess_exec(*command)


async def build_target(target: Target):
    if target.name in _build_tasks:
        await _build_tasks[target.name]  # wait for the already-running build
        return

    async def _do_build():
        deps = [
            _target_builders[dep] for dep in target.depends if dep in _target_builders
        ]
        await asyncio.gather(*[build_target(dep) for dep in deps])
        if not must_build(target):
            print(f"{target.name} is up to date.")
            return

        command = target.get_command()
        display = target.path if target.path else target.name
        print(f"{display}:", *command)
        result = await run_task(*command, silent=True)
        await result.wait()
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode or -1, "".join(command)
            )

    task = asyncio.ensure_future(_do_build())
    _build_tasks[target.name] = task
    await task


async def build_all_targets():
    await asyncio.gather(*[build_target(t) for t in _implicit_targets])


async def pmain():
    parser = argparse.ArgumentParser(
        prog="PMake", description="Python-Based Makefile alternative"
    )
    parser.add_argument(
        "-f", default="PMakefile.py", type=str, help="Path to PMakefile to evaluate"
    )
    parser.add_argument(
        "--target",
        required=False,
        nargs="+",
        help="Name of target or targets to run, defaults to all non-explicit targets",
    )

    args = parser.parse_args()
    pmakefile = Path(args.f)

    if not pmakefile.is_file():
        raise RuntimeError(f"Could not locate file {pmakefile}")
    content = pmakefile.read_text()

    global __name__
    name_backup = __name__
    __name__ = "PMakefile"
    exec(content, globals())  # Trust the PMakefile you are running!
    __name__ = name_backup

    target_displays = [
        f"{name} (explicit)" if t.explicit else name
        for name, t in sorted(_all_targets.items(), key=lambda item: item[1].explicit)
    ]
    print("Loaded targets:", ", ".join(target_displays))

    if args.target is not None:
        await asyncio.gather(*[build_target(_all_targets[t]) for t in args.target])
    else:
        await build_all_targets()


if __name__ == "__main__":
    asyncio.run(pmain())
