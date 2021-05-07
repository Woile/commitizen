[![Github Actions](https://github.com/commitizen-tools/commitizen/workflows/Python%20package/badge.svg?style=flat-square)](https://github.com/commitizen-tools/commitizen/actions)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![PyPI Package latest release](https://img.shields.io/pypi/v/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)
[![PyPI Package download count (per month)](https://img.shields.io/pypi/dm/commitizen?style=flat-square)](https://pypi.org/project/commitizen/)
[![Supported versions](https://img.shields.io/pypi/pyversions/commitizen.svg?style=flat-square)](https://pypi.org/project/commitizen/)
[![homebrew](https://img.shields.io/homebrew/v/commitizen?color=teal&style=flat-square)](https://formulae.brew.sh/formula/commitizen)
[![Codecov](https://img.shields.io/codecov/c/github/commitizen-tools/commitizen.svg?style=flat-square)](https://codecov.io/gh/commitizen-tools/commitizen)

![Using commitizen cli](images/demo.gif)

---

**Documentation:** [https://commitizen-tools.github.io/commitizen/](https://commitizen-tools.github.io/commitizen/)

---

## About

Commitizen is a tool designed for teams.

Its main purpose is to define a standard way of committing rules
and communicating it (using the cli provided by commitizen).

The reasoning behind it is that it is easier to read, and enforces writing
descriptive commits.

Besides that, having a convention on your commits makes it possible to
parse them and use them for something else, like generating automatically
the version or a changelog.

### Commitizen features

- Command-line utility to create commits with your rules. Defaults: [Conventional commits][conventional_commits]
- Display information about your commit rules (commands: schema, example, info)
- Bump version automatically using [semantic versioning][semver] based on the commits. [Read More](./bump.md)
- Generate a changelog using [Keep a changelog][keepchangelog]

## Requirements

Python 3.6+

[Git][gitscm] `1.8.5.2`+

## Installation

Global installation

```bash
sudo pip3 install -U Commitizen
```

### Python project

You can add it to your local project using one of these:

```bash
pip install -U commitizen
```

```bash
poetry add commitizen --dev
```

### macOS

On macOS, it can also be installed via [homebrew](https://formulae.brew.sh/formula/commitizen):

```bash
brew install commitizen
```

## Usage

### Committing

Run in your terminal

```bash
cz commit
```

or the shortcut

```bash
cz c
```

### Integrating with Pre-commit
Commitizen can lint your commit message for you with `cz check` and `cz commit`.
You can integrate this in your [pre-commit](https://pre-commit.com/) config with:

```yaml
---
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: master
    hooks:
      - id: commitizen
        stages: [commit-msg]
      - id: commitizen-prepare-commit-msg
        stages: [prepare-commit-msg]
```

After the configuration is added, you'll need to run

```sh
pre-commit install --hook-type commit-msg
```

Read more about the `check` command [here](https://commitizen-tools.github.io/commitizen/check/).

### Help

```bash
$ cz --help
usage: cz [-h] [--debug] [-n NAME] [--version]
          {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version}
          ...

Commitizen is a cli tool to generate conventional commits.
For more information about the topic go to https://conventionalcommits.org/

optional arguments:
  -h, --help            show this help message and exit
  --debug               use debug mode
  -n NAME, --name NAME  use the given commitizen (default:
                        cz_conventional_commits)
  --version             get the version of the installed commitizen

commands:
  {init,commit,c,ls,example,info,schema,bump,changelog,ch,check,version}
    init                init commitizen configuration
    commit (c)          create new commit
    ls                  show available commitizens
    example             show commit example
    info                show information about the cz
    schema              show commit schema
    bump                bump semantic version based on the git log
    changelog (ch)      generate changelog (note that it will overwrite
                        existing file)
    check               validates that a commit message matches the commitizen
                        schema
    version             get the version of the installed commitizen or the
                        current project (default: installed commitizen)
```

## Setting up bash completion

When using bash as your shell (limited support for zsh, fish, and tcsh is available), Commitizen can use [argcomplete](https://kislyuk.github.io/argcomplete/) for auto-completion. For this argcomplete needs to be enabled.

argcomplete is installed when you install Commitizen since it's a dependency.

If Commitizen is installed globally, global activation can be executed:

```bash
sudo activate-global-python-argcomplete
```

For permanent (but not global) Commitizen activation, use:

```bash
register-python-argcomplete cz >> ~/.bashrc
```

For one-time activation of argcomplete for Commitizen only, use:

```bash
eval "$(register-python-argcomplete cz)"
```

For further information on activation, please visit the [argcomplete website](https://kislyuk.github.io/argcomplete/).

## Third-Party Commitizen Templates

See [Third-Party Commitizen Templates](third-party-commitizen.md).

## FAQ

### Why are `revert` and `chore` valid types in the check pattern of cz conventional_commits but not types we can select?

`revert` and `chore` are added to the "pattern" in `cz check` in order to prevent backward errors, but officially they are not part of conventional commits, we are using the latest [types from Angular](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#type) (they used to but were removed).
However, you can create a customized `cz` with those extra types. (See [Customization](https://commitizen-tools.github.io/commitizen/customization/))

See more discussion in issue [#142](https://github.com/commitizen-tools/commitizen/issues/142) and [#36](https://github.com/commitizen-tools/commitizen/issues/36)

### How to handle revert commits?

```sh
git revert --no-commit <SHA>
git commit -m "revert: foo bar"
```

## Contributing

See [Contributing](contributing.md)

[conventional_commits]: https://www.conventionalcommits.org
[semver]: https://semver.org/
[keepchangelog]: https://keepachangelog.com/
[gitscm]: https://git-scm.com/downloads
