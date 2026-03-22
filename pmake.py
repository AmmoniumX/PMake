import asyncio
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Target:
    path: Path
    depends: list[Path] = field(default_factory=list)
    command: Callable[[Target], list[str]] = None  # type: ignore


target_builders: dict[Path, Target] = dict()


def target(path: Path, depends: list[Path], command: Callable[[Target], list[str]]):
    t = Target(path, depends, command)
    if t.path in target_builders:
        raise Exception("path already has a target")
    target_builders[t.path] = t
    return t


async def compile_dep(dep: Target):
    command = dep.command(dep)
    print("exec:", command)
    proc = await asyncio.create_subprocess_exec(*command)
    await proc.wait()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode or -1, dep.path)


async def compile_impl(target: Target):

    deps = [target_builders[dep] for dep in target.depends if not dep.is_file()]
    await asyncio.gather(*[compile_impl(dep) for dep in deps])
    if target.path.is_file():
        return

    print(f"Compiling {target.path}...")
    result = await asyncio.create_subprocess_exec(*target.command(target))
    await result.wait()
    if result.returncode is None or result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode or -1, target.path)


async def compile(target: Target):
    if target.path.is_file():
        print(f"{target.path} exists. Nothing to compile")
        return
    await compile_impl(target)


def compile_cmd(target: Target) -> list[str]:
    inputs = [str(dep) for dep in target.depends]
    return ["gcc", *inputs, "-o", str(target.path)]


main = target(path=Path("./main"), depends=[Path("./main.c")], command=compile_cmd)
asyncio.run(compile(main))
