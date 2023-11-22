# How To Contribute

`gapper` welcomes everyone to contribute to the project. There are many ways to contribute. 
You can open up issues when you find bugs or have feature requests. You can also contribute
code to the project. This document contains the guidelines for contributing to the project.

## Prerequisite

We assume you have `Python>=3.12` and [`poetry`](https://python-poetry.org/) is installed on your computer. 

/// details | Python Version Management
We recommend using [`pyenv`](https://github.com/pyenv/pyenv) to manage your python version. 
You can find its installation instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
///

## Setup

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the [repo (https://github.com/FlickerSoul/gapper)](https://github.com/FlickerSoul/gapper) to your account.
2. Clone the repo by `git clone https://github.com/<your_user_name>/gapper.git`.
3. Install dependencies using `poetry install`.
4. Set up the pre-commit hooks by `pre-commit install --hook-type pre-commit --hook-type pre-push`. See <a href="#code-style">Code Style</a>.
5. (Optionally but recommended) Install the IDE plugins for `ruff`:
   - If you're using IDEs from JetBrains, please install the [ruff plugin](https://plugins.jetbrains.com/plugin/20574-ruff). 
   - If you're using vim/neovim, please install the [ruff LSP server](https://github.com/astral-sh/ruff-lsp) and enable it.
   - If you're using VSCode, please install the [ruff VSCode extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).
6. Write code, commit.
7. Test your code by running `pytest tests`. See <a href="#testing">Testing</a>.
    - Integrations tests like testing CLI commands and GUI can be slow. You can ignore them by adding 
      `--ignore-glob=*integration_test.py` flag to your `pytest` command. 
    - Note that some tests require you set up gradescope account details, or otherwise they will be skipped
8. Push to your account.
9. Open a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

## Code Style

If you have pre-commit hooks installed, you're good to go. 
The hooks will automatically check your code style and notify you if something went wrong. 

If you're using any kind of IDEs, please install the corresponding plugins from the instructions above. 

We are currently not checking document strings and this will be enforced in the future.

`gapper` uses [`ruff`](https://github.com/astral-sh/ruff?tab=readme-ov-file) as the formatter and linter. 
The configuration is encoded in the `pyproject.toml` located under the root of this project. You should run 
`ruff src tests` to lint the style of your code, and use `ruff format src tests` to format your code. 
You might be prompt to use the `--fix` flag to auto-fix some of the problems, and please do when you find so. 

## Testing

Testing is done using `pytest` and several extensions include `pytest-mock`, `pytest-asyncio`, and `pytest-cov`. 

As mentioned above, some integrations can be slow to test, including CLI testing and GUI testing. You can find those 
integrations by searching `*integration_test.py` in the project directory. 

The pre-commit hook ignores integration tests when you commit, but checks them when you push. This helps us do quick 
commits without waiting for testing while ensuring code qualities. This implies two things: 

1. You have to pass tests before committing/pushing.
2. Please do not include lengthy tests into the commit hook, as this will cost developers time. 
