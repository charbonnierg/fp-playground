# Function Programming in Python

## Installation

This project is not yet published under a PyPi-compatible registry such as `pypi.org` or Azure Artifact Feed.

In order to be installed, you must have pull access for the git repository. You can either:

- Clone the repository and install (for developers):

    ```bash
    # Clone the git repository
    git clone <origin_url> fp/
    # Enter the repository directory
    cd fp/
    # Create a new virtual environment
    python3 -m venv .venv --upgrade-deps
    # Activate freshly created virtual environment
    source .venv/bin/activate
    # Install local project in editable mode
    python -m pip install -e .[dev]
    ```

    > For Python 3.8 users, `--upgrade-deps` option is not available. Simply don't use it, and instead
    > run `pip install -U pip setuptools wheel` within virtual environment after it is created.

- Install the project in the environment of your choice (for users):

    ```bash
    python -m pip install git+ssh://<origin_url>
    ```

    > The command above will install the package into the environment of the current python interpreter.

## Usage

Checkout [examples](./examples) in order to learn about usage.

## Contribute

Developers must ensure that the CI tests pass locally before pushing a commit.

An [invoke task](https://www.pyinvoke.org/) is available to quickly run checks and tests:

```bash
inv ci
```

> The virtual environment of the project must be sourced before running commands with `inv`.

Several other tasks are available to developers, run `inv --list` to list them all.

> During development, it's possible to use the `-w` option with `inv ci` command in order to allow formatters to sort imports and reformat code:
> ```bash
> inv ci -w
> ```
> In CI pipeline, `-w` should never be used as formatters should only be used to check the code and not modify it.

## IDE Integration

The recommended IDE for this project is VSCode, because [`pyright`](https://github.com/microsoft/pyright) is used to perform type checking,
and VSCode uses [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) which is powered by [`pyright`](https://github.com/microsoft/pyright).

Below is the config I use for this project:

```json
{
    "files.exclude": {
        "**/.git": true,
        "**/.svn": true,
        "**/.hg": true,
        "**/CVS": true,
        "**/.DS_Store": true,
        "**/Thumbs.db": true,
        "**/__pycache__": true,
        "**/.venv": true,
        "**/*.egg-info": true,
        "**/.pytest_cache": true,
        "**/.mutmut-cache": true,
        "**/.mypy_cache": true,
        "**/.coverage": true,
        "**/coverage.xml": true,
        "**/coverage-report": true,
        "**/junit": true,
        "**/build": true,
        "**/.vscode": true,
        "**/dist": true,
    },
    "editor.formatOnSave": true,
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        },
    },
    "isort.args": [
        "--profile",
        "black"
    ],
    "python.analysis.enablePytestSupport": true,
    "python.analysis.inlayHints.callArgumentNames": false,
    "python.analysis.inlayHints.functionReturnTypes": true,
    "python.analysis.inlayHints.variableTypes": true,
    "python.analysis.inlayHints.pytestParameters": true,
    "python.analysis.autoImportCompletions": true,
    "python.analysis.autoFormatStrings": true,
    "python.analysis.autoSearchPaths": true,
    "python.analysis.indexing": true,
    "python.testing.pytestEnabled": true
}
```