# Packaging

Here we write tips related to packaging

[Official documentation](https://python-poetry.org/docs)

## Poetry

### configuration (venv, cache, pypi)

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

### environment info

```cmd
poetry env info
```


### Build and publish

```cmd
poetry update
poetry build
poetry publish
```


## bump2version

This helps to version.


Note: Once pypi is updated you can never use the same version number even if you
  delete files and recreate repo


```cmd
REM bump2version major
REM bump2version minor
bump2version patch
git push
git push --tags
poetry build
poetry publish
```


## deleting releases from github tags and pypi

Sometimes we might need to delete bad releases. So this is how we do it.

Note test and then bump version. In case later bugs are realized we can still delete it.

```cmd
git push --delete origin v0.1.2
git tag -d v0.1.2
```

For PyPi you manually delete realese or Yank it...
Note that releasing is serious so do it rarely ...
