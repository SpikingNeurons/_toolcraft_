"""
Design considerations:
+ Only one level of nesting supported for tensors
  + you can have NamedTuple fields to be tensors or a dict of tensors
    this ensures proper working in eager and non-eager mode ... as looks like
    internally tensorflow flattens nested tensors array ... also in eager mode
    it does not retain tensor names and auto names the tensors ... so it is
    safe bet to have one level of tensors ... and if any nesting is necessary
    play with dictionary keys ;)
+ Everywhere we communicate with NamedTuples
  + because they are awesome
  + we can inject util methods like a normal python class ... this is not
    possible with tuple, dict and namedtuple .... only t.NamedTuple
    allows this hack ;)
"""
from . import handler
from . import __base__
from .__base__ import Dataset, \
    PreparedFileGroup, FosteredFileGroup, NPY_OR_TENSOR
