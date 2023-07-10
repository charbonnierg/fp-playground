from __future__ import annotations

import os
from pathlib import Path
from shutil import rmtree

from invoke.context import Context
from invoke.tasks import task

VENV_DIR = Path(__file__).parent.resolve(True) / ".venv"

if os.name == "nt":
    VENV_PYTHON = VENV_DIR.joinpath("Scripts/python.exe").as_posix()
else:
    VENV_PYTHON = VENV_DIR.joinpath("bin/python").as_posix()


def run_or_display(c: Context, cmd: str, dry_run: bool):
    if dry_run:
        print(cmd)
    else:
        c.run(cmd)


@task
def requirements(c: Context, with_hashes: bool = False, dry_run: bool = False):
    """Generate requirementx.txt using piptools compile command.

    WARNING: piptools must be installed in order to run this command.
    It can be installed using pip: 'python -m pip install pip-tools'
    """
    cmd = (
        f"{VENV_PYTHON} -m piptools compile"
        " --no-header"
        " --output-file=requirements.txt"
        " --resolver=backtracking"
    )
    if with_hashes:
        cmd += " --generate-hashes"
    cmd += " pyproject.toml"
    run_or_display(c, cmd, dry_run=dry_run)


@task
def build(c: Context, docs: bool = False, dry_run: bool = False):
    """Build sdist and wheel, and optionally build documentation."""
    python_build_cmd = f"{VENV_PYTHON} -m build --no-isolation --outdir dist ."
    docs_build_cmd = f"{VENV_PYTHON} -m mkdocs build -d dist/documentation"
    run_or_display(c, python_build_cmd, dry_run=dry_run)
    if docs:
        if not dry_run:
            rmtree("dist/documentation", ignore_errors=True)
        run_or_display(c, docs_build_cmd, dry_run=dry_run)


@task
def wheelhouse(
    c: Context, clean: bool = False, compress: bool = False, dry_run: bool = False
):
    """Build wheelhouse for the project"""
    wheelhouse_cmd = f"{VENV_PYTHON} -m pip wheel . -w dist/wheelhouse"
    compress_cmd = "tar -czf dist/wheelhouse.tar.gz -C dist wheelhouse"
    if not dry_run:
        Path("dist").mkdir(exist_ok=True)
    if clean and not dry_run:
        rmtree("dist/wheelhouse", ignore_errors=True)
    run_or_display(c, wheelhouse_cmd, dry_run=dry_run)
    if not dry_run:
        rmtree("build", ignore_errors=True)
    if compress:
        run_or_display(c, compress_cmd, dry_run=dry_run)


@task
def docs(c: Context, watch: bool = True, port: int = 8000, dry_run: bool = False):
    """Serve the documentation in development mode."""
    cmd = f"{VENV_PYTHON} -m mkdocs serve -a localhost:{port}"
    if watch:
        cmd += " --livereload --watch docs/ --watch src"
    else:
        cmd += "  --no-livereload"
    run_or_display(c, cmd, dry_run=dry_run)


@task
def test(
    c: Context,
    cov: str = "",
    e2e: bool = False,
    markers: str = "",
    pattern: str = "",
    x: bool = False,
    v: bool = False,
    vv: bool = False,
    vvv: bool = False,
    dry_run: bool = False,
):
    """Run tests using pytest and optionally enable coverage."""
    cmd = f"{VENV_PYTHON} -m pytest"
    if x:
        cmd += " -x"
    if vvv:
        cmd += " -vvv"
    elif vv:
        cmd += " -vv"
    elif v:
        cmd += " -v"
    else:
        cmd += " -q"
    if markers:
        cmd += f" -m {markers}"
    if pattern:
        cmd += f" -p {pattern}"
    if cov:
        cmd += f" --cov {cov} --cov-report=html:coverage-report --cov-report=term-missing --cov-fail-under=100"
    if e2e:
        cmd += " tests"
    else:
        cmd += " tests/fp"
    run_or_display(c, cmd, dry_run=dry_run)


@task
def coverage(c: Context, run: bool = False, port: int = 8000, dry_run: bool = False):
    """Serve code coverage results and optionally run tests before serving results"""
    if run:
        test(c, True, dry_run=dry_run)
    cmd = f"{VENV_PYTHON} -m http.server {port} --dir coverage-report"
    run_or_display(c, cmd, dry_run)


@task
def check(c: Context, dry_run: bool = False):
    """Run pyright typechecking."""
    cmd = "pyright"
    run_or_display(c, cmd, dry_run=dry_run)


@task
def fmt(c: Context, check: bool = False, dry_run: bool = False):
    """Format source code using black and isort."""
    opts = " --check" if check else ""
    run_or_display(c, f"{VENV_PYTHON} -m isort .{opts}", dry_run=dry_run)
    run_or_display(c, f"{VENV_PYTHON} -m black .{opts}", dry_run=dry_run)


@task
def lint(c: Context, dry_run: bool = False):
    """Lint source code using flake8."""
    run_or_display(c, f"{VENV_PYTHON} -m flake8 .", dry_run=dry_run)
    print("All done! ✨ 🍰 ✨")


@task
def ci(
    c: Context,
    w: bool = False,
    e2e: bool = False,
    v: bool = False,
    vv: bool = False,
    vvv: bool = False,
):
    """Ensure checks performed in CI will not fail before pushing to remote"""
    print("Formatting... ⏳")
    fmt(c, check=not w)
    print("Linting... ⏳")
    lint(c)
    print("Type checking... ⏳")
    check(c)
    print("Testing... ⏳")
    test(c, e2e=e2e, v=v, vv=vv, vvv=vvv, cov="src/fp")


@task
def mut(c: Context):
    """Run mutation testing using mutmut."""
    cmd = "mutmut run"
    c.run(cmd)
