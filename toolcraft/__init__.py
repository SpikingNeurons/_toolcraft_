"""
Top-level package for toolcraft.

Resolving __version__
  + This cannot be hardcoded also the external setup files are not shipped so we use this solution
    https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
  + Read the discussion here as to why this is so tedious
    https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
  + Note that bump2version tends to modify the string so always use poetry
"""

__author__ = """Praveen Kulkarni"""
__email__ = 'praveenneuron@gmail.com'

# Note that this is done as code cannot know the version number and it is the job of pyproject.toml
try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version(__name__)
except PackageNotFoundError as pnf:
    __version__ = 'cannot estimate version'
except ModuleNotFoundError as mnf:
    __version__ = 'cannot estimate version'
