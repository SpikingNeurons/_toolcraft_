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

    @s.StoreField()
    def f(
        self, mode: s.MODE_TYPE, epoch: int
    ) -> pa.Table:
        ...


a = A()

print(A.f)
print(A().f)

print(s.is_store_field(A.f))
print(s.is_store_field(A().f))
print(hasattr(A, 'f'))
print(hasattr(A(), 'f'))
