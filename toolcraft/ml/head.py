"""
This module holds special Blocks that are heads.
They are inspired by
>>> # noinspection PyShadowingNames
>>> import tensorflow as tf
>>> tf.estimator.Head

Some things that we do in Head:
+ Metrics
    Based on head type we add specific metrics automatically and give users
    options to switch on and off specific metrics. Note that this means that we
    cannot pass metrics to Head instead we can select them.
    >>> tf.estimator.Head.metrics
    todo: the extra regularization passes to loss can be captured here as
      metric if needed
+ Losses
    Objects related to the losses will be auto handled by Heads. Plus if you
    need to select custom or add extra regularized losses then that needs to
    be done vis dataclass fields. Check:
    >>> tf.estimator.Head.loss
    todo: add support for adding extra regularized losses
+ Optimizers, Learning Rate Schedulers
    Should be selected via dataclass fields

"""
import tensorflow as tf
import tensorflow.keras as tk
import typing as t
import abc
import dataclasses
from tensorflow.keras.layers import Layer

from .. import util
from .. import error as e
from .__base__ import Head


@dataclasses.dataclass(frozen=True)
class MultiClassHead(Head):

    @property
    @util.CacheResult
    def metrics(self) -> t.List[tk.metrics.Metric]:
        return [
            tk.metrics.SparseCategoricalAccuracy(),
            tk.metrics.SparseCategoricalCrossentropy(),
        ]

    def build(self, *, inputs: Layer) -> Layer:
        # check
        if self.model.num_classes == 2:
            e.code.NotAllowed(
                msgs=[
                    f"Please use binary classifier head when num_classes is 2"
                ]
            )
        # return
        return tk.layers.Dense(
            units=self.model.num_classes, activation='softmax',
            name='softmax'
        )(inputs)


@dataclasses.dataclass(frozen=True)
class BinaryClassHead(Head):

    @property
    @util.CacheResult
    def metrics(self) -> t.List[tk.metrics.Metric]:
        return [
            tk.metrics.BinaryAccuracy(),
            tk.metrics.BinaryCrossentropy()
        ]

    def build(self, *, inputs: Layer) -> Layer:
        # check
        if self.model.num_classes > 2:
            e.code.NotAllowed(
                msgs=[
                    f"Please use multi-class classifier head when num_classes "
                    f"is greater than 2"
                ]
            )
        # return
        return tk.layers.Dense(
            units=1, activation='sigmoid',
            name='sigmoid'
        )(inputs)