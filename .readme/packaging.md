# Packaging

Here we write tips related to packaging

[Official documentation](https://python-poetry.org/docs)

## Poetry

### Installation

Poetry should not be installed from pip
So use this
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```
Then you need to get poetry in your path
So add below code to PATH system environment variable
```
%USERPROFILE%\.poetry\bin
```

Check poetry

```
poetry --version
```

Poetry update

```
poetry self update
```

Poetry uninstall then check

https://python-poetry.org/docs/#enable-tab-completion-for-bash-fish-or-zsh

### Configuration (venv, cache, pypi)

https://python-poetry.org/docs/configuration/

+ poetry has venv that can be setup with `poetry config`
+ note that the poetry config is specific to local environment and nothing to do with repo
+ pypi token will not be save to repo even if you specify config to be `--local`

We will do certain things so that we fully control poetry via `poetry.toml`
That is the config file will reside locally. That is by using `--local`

```cmd
REM check config
poetry config --list

REM we want to use virtual env locally
poetry config virtualenvs.create true --local

REM keep cache locally inside repo ... note venv will go inside it
poetry config cache-dir ".poetry_cache" --local

REM configure pypi token
poetry config pypi-token.pypi <token from pypi>
```

### Environment info

```cmd
poetry env info
```


### Package managing tasks

Note that click (or else typer) are cli tools provided by library we are deploying.
To manage th library itself we use `invoke`.
Also note that it is part of dev dependencies and will never be distributed when packaged.

Please refer `tasks.py`

Calling invoke tasks is easy and must be done with poetry

```
poetry run invoke docs
poetry run invoke coverage
poetry run invoke test
poetry run invoke lint
poetry run invoke clean
poetry run invoke dist
...
```


### Build and publish

```cmd
poetry update
poetry build
poetry publish
```


### Versioning

This helps to version.

Note: Once pypi is updated you can never use the same version number even if you
  delete files and recreate repo

Note: bump rules are:
  patch, minor, major, prepatch, preminor, premajor, prerelease

```cmd
poetry version

poetry version <bump_rule>

poetry build

poetry publish

```

Note: for poetry publish from local desk you need to set API token from pypi

```
poetry config pypi-token.pypi my-token
```


### Deleting releases from github tags and pypi

Sometimes we might need to delete bad releases. So this is how we do it.

Note test and then bump version. In case later bugs are realized we can still delete it.

```cmd
git push --delete origin v0.1.2
git tag -d v0.1.2
```

For PyPi you manually delete realese or Yank it...
Note that releasing is serious so do it rarely ...
