"""
Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke
"""
import shutil
import platform

from invoke import task
from pathlib import Path
import webbrowser


ROOT_DIR = Path(__file__).parent
SETUP_FILE = ROOT_DIR.joinpath("setup.py")
TEST_DIR = ROOT_DIR.joinpath("tests")
SOURCE_DIR = ROOT_DIR.joinpath("toolcraft")
TOX_DIR = ROOT_DIR.joinpath(".tox")
COVERAGE_FILE = ROOT_DIR.joinpath(".coverage")
COVERAGE_DIR = ROOT_DIR.joinpath("htmlcov")
COVERAGE_REPORT = COVERAGE_DIR.joinpath("index.html")
SPHINX_DIR = ROOT_DIR.joinpath(".sphinx")
SPHINX_BUILD_DIR = SPHINX_DIR.joinpath(".build")
DOCUSAURUS_DIR = ROOT_DIR.joinpath(".website")
NOTEBOOKS_DIR = ROOT_DIR.joinpath(".notebooks")
SCRIPTS_DIR = ROOT_DIR.joinpath("scripts")
SPHINX_INDEX = SPHINX_BUILD_DIR.joinpath("index.html")
PYTHON_DIRS = [str(d) for d in [SOURCE_DIR, TEST_DIR]]


def _delete_file(file):
    try:
        file.unlink(missing_ok=True)
    except TypeError:
        # missing_ok argument added in 3.8
        try:
            file.unlink()
        except FileNotFoundError:
            pass


def _run(c, command):
    return c.run(command, pty=platform.system() != 'Windows')


@task(help={'check': "Checks if source is formatted without applying changes"})
def format(c, check=False):
    """
    Format code
    """
    python_dirs_string = " ".join(PYTHON_DIRS)
    # Run yapf
    yapf_options = '--recursive {}'.format('--diff' if check else '--in-place')
    _run(c, "yapf {} {}".format(yapf_options, python_dirs_string))
    # Run isort
    isort_options = '--recursive {}'.format(
        '--check-only --diff' if check else '')
    _run(c, "isort {} {}".format(isort_options, python_dirs_string))


@task
def lint_flake8(c):
    """
    Lint code with flake8
    """
    _run(c, "flake8 {}".format(" ".join(PYTHON_DIRS)))


@task
def lint_pylint(c):
    """
    Lint code with pylint
    """
    _run(c, "pylint {}".format(" ".join(PYTHON_DIRS)))


@task(lint_flake8, lint_pylint)
def lint(c):
    """
    Run all linting
    """


@task
def test(c):
    """
    Run tests
    """
    _run(c, "pytest")


@task(help={'publish': "Publish the result via coveralls"})
def coverage(c, publish=False):
    """
    Create coverage report
    """
    _run(c, "coverage run --source {} -m pytest".format(SOURCE_DIR))
    _run(c, "coverage report")
    if publish:
        # Publish the results via coveralls
        _run(c, "coveralls")
    else:
        # Build a local report
        _run(c, "coverage html")
        webbrowser.open(COVERAGE_REPORT.as_uri())


@task(
    help={
        'launch': "Launch documentation in the web browser",
        'static': "Will build static website"
    }
)
def docs(c, launch=True, static=True):
    """
    Generate documentation.

    Make sure that you have docusaurus website classic template setup as given below.
    Note that the .website dir must not be present before creating

    ```
    npx @docusaurus/init@latest init .website classic
    cd .website
    yarn run start
    ```

    You can also do to build static website and serve locally.
    ```
    yarn run build
    npm run serve
    ```
    """
    # build sphinx
    _run(c, "sphinx-build -b html {} {}".format(SPHINX_DIR, SPHINX_BUILD_DIR))

    # Note we assume that the docusaurus website is already there at .website
    ...

    # parse sphinx
    _i = SPHINX_BUILD_DIR
    _o = DOCUSAURUS_DIR
    _parse_sphinx = SCRIPTS_DIR / 'parse_sphinx.py'

    _run(c, f"python {_parse_sphinx.as_posix()} -i {_i.as_posix()} -o {_o.as_posix()}")

    # copy sphinx js files to docusaurus js folder
    for _js in [
        'documentation_options.js', 'jquery.js', 'underscore.js',
        'doctools.js', 'language_data.js', 'searchtools.js',
    ]:
        _src = SPHINX_BUILD_DIR / '_static' / _js
        _dst = DOCUSAURUS_DIR / 'static' / _js
        _dst.parent.mkdir(parents=True, exist_ok=True)
        # if _js == 'searchtools.js':
        #     _src = SPHINX_BUILD_DIR / _js
        _run(c, f"cp {_src.as_posix()} {_dst.as_posix()}")

    # copy module sources
    _i = SPHINX_BUILD_DIR / '_sources'
    _o = DOCUSAURUS_DIR / 'static' / '_sphinx-sources'
    _run(c, f"cp -r {_i.as_posix()} {_o.as_posix()}")

    # parse notebooks
    _i = NOTEBOOKS_DIR
    _o = DOCUSAURUS_DIR
    _parse_nb = SCRIPTS_DIR / 'parse_notebooks.py'
    _run(c, f"python {_parse_nb.as_posix()} -i {_i.as_posix()} -o {_o.as_posix()}")

    _run(c, f"cd .website && yarn install")

    if static:
        _run(c, f"cd .website && yarn run build")
    if launch:
        _run(c, f"cd .website && yarn run serve")


@task
def clean_docs(c):
    """
    Clean up files from documentation builds
    """
    _run(c, "rm -fr {}".format(SPHINX_BUILD_DIR))


@task
def clean_build(c):
    """
    Clean up files from package building
    """
    _run(c, "rm -fr build/")
    _run(c, "rm -fr dist/")
    _run(c, "rm -fr .eggs/")
    _run(c, "find . -name '*.egg-info' -exec rm -fr {} +")
    _run(c, "find . -name '*.egg' -exec rm -f {} +")


@task
def clean_python(c):
    """
    Clean up python file artifacts
    """
    _run(c, "find . -name '*.pyc' -exec rm -f {} +")
    _run(c, "find . -name '*.pyo' -exec rm -f {} +")
    _run(c, "find . -name '*~' -exec rm -f {} +")
    _run(c, "find . -name '__pycache__' -exec rm -fr {} +")


@task(help={'full-report': "Provides more detailed report"})
def check_safety(c, full_report=True):
    """
    Performs safety checks
    """
    if full_report:
        _run(c, "safety check --full-report")
    else:
        _run(c, "safety check")


@task
def clean_tests(c):
    """
    Clean up files from testing
    """
    _delete_file(COVERAGE_FILE)
    shutil.rmtree(TOX_DIR, ignore_errors=True)
    shutil.rmtree(COVERAGE_DIR, ignore_errors=True)


@task(pre=[clean_build, clean_python, clean_tests, clean_docs])
def clean(c):
    """
    Runs all clean sub-tasks
    """
    pass


@task(clean)
def dist(c):
    """
    Build source and wheel packages
    """
    _run(c, "poetry build")


@task(pre=[clean, dist])
def release(c):
    """
    Make a release of the python package to pypi
    """
    _run(c, "poetry publish")
