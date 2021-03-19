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
