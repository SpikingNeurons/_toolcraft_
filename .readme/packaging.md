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
poetry run invoke check-safety
...
```

Note: The task method names that have under-score will
  become `-` when invoking them


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


## Upgrading pip in poetry

Remember poetry is sepeately installled and not via pip
So latest poetry still can have oild pip
So the dark workaround is

```
poetry run pip install pip -U
```

Refer the discussion here ... it might take time


## Deleting releases from github tags and pypi

Sometimes we might need to delete bad releases. So this is how we do it.

Note test and then bump version. In case later bugs are realized we can still delete it.

```cmd
git push --delete origin v0.1.2
git tag -d v0.1.2
```

For PyPi you manually delete realese or Yank it...
Note that releasing is serious so do it rarely ...


## PyUp (Validating dependencies)

Poetry does not give out requirements file
PyUp cannot work with poetry
So we have added a task `check-safety` and with help of invoke we can call it

```
poetry run invoke check-safety
poetry add insecure-package
poetry run invoke check-safety
poetry remove insecure-package
poetry run invoke check-safety
```

## accessing pyproject inside __init__

We need to sometimes use project info inside source code.
So we can either modify init file before release like bump2version
Check todo there anyways

## Docusaurus - Sphinx

We rely on this plugin
https://npm.io/package/docusaurus-plugin-sphinx-docs

```
module.exports = {
  // ...
  plugins: ['@dmitryvinn/docusaurus-plugin-sphinx-docs'],
};
```

Resources
The plugin is built based on scripts created by BoTorch team.
https://github.com/pytorch/botorch/tree/master/scripts


Check `index.rst` and how `automodule` can import doc from python code
+ https://github.com/pytorch/botorch/blob/master/sphinx/source/index.rst
+ https://github.com/pytorch/botorch/blob/master/sphinx/source/models.rst

### Setup Sphinx

This is easy and already committed in required way in repo

### Setup Docusaurus

#### Get Node [link](https://nodejs.org/en/download/)

#### Install yarn
```
npm install --global yarn
yarn --version
```

#### Create project website
https://v2.docusaurus.io/docs/installation

```
npx @docusaurus/init@latest init .website classic
cd .website
yarn run start
```

Now we can build so that to get static website in `/build` directory

```
yarn run build
```

Now you can serve it locally

```
npm run serve
```


#### install plugin
https://npm.io/package/docusaurus-plugin-sphinx-docs

First we will add npm package for plugin

This does not work :(
```
yarn add docusaurus-plugin-sphinx-docs
```

Then you add it in your site's docusaurus.config.js's plugins option:

```
plugins: ['@dmitryvinn/docusaurus-plugin-sphinx-docs'],
```


## TODO

### Poetry version should bump version in __init__

bump2version does it but poetry doesn't.
Can we just make that ourselves.

### CI/CD pipeline actions
Should do CI with travis etc.
Needed when we want to make packages for different python versions.
Right now our code is fully on python so we rely on sbist
That is we distribute source

### GUI for invoke tasks

Make some GUI for invoke tasks

### Release to github tags

Should do this alongside `CI/CD pipeline actions` task above

### Invoke tasks

#### Check Safety invoke task

check-safety invoke task jsut spits out the text log
Grab the output and list out vulnerable package and raise
error so that deployment or publish fails

#### make task to delete tag releases and files on pypi

#### make task to git pull version build publish deploy
