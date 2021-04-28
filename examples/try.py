import dataclasses
import numpy as np
import time
import datetime
import typing as t
from dearpygui import core as dpg
import pyarrow as pa

from toolcraft import gui, util
from toolcraft import storage as s

class A:

    def __init__(self):
        self.a = 333

class AA:

    def __init__(self):
        self.aa = A()


aa= AA()
pp = util.rgetattr(aa, 'aa.a')
print(pp)
util.rsetattr(aa, 'aa.a', 444)
pp = util.rgetattr(aa, 'aa.a')
print(pp)
print(util.rhasattr(aa, 'aa.a'))
