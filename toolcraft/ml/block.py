"""
This will evolve in package later ...
Simple constructs that can be used to build models ...

A block can be build by composing layers and extending tf.keras.Model
So it will be better to have that mechanism as it is  ...

Get inspirations from autokeras library
>>> import autokeras as ak
>>> ak.ConvBlock

todo: Can we have something like keras-tuners that is also used by autokeras
"""
import dataclasses
import typing as t
import tensorflow.keras as tk
from tensorflow.keras import layers
from tensorflow.python.keras.layers import convolutional

from .. import settings
from .. import error as e
from .__base__ import Block


@dataclasses.dataclass(frozen=True)
class Dense(Block):
    """
    Refer to:
    >>> tk.layers.Dense
    """
    units: int
    activation: str

    # noinspection DuplicatedCode
    def build(self, *, inputs: layers.Layer) -> layers.Layer:
        # build
        return tk.layers.Dense(
            units=self.units, activation=self.activation,
            name=self.name
        )(inputs)


@dataclasses.dataclass(frozen=True)
class Conv(Block):
    """
    Refer to
    >>> tk.layers.Conv1D
    >>> tk.layers.Conv2D
    >>> tk.layers.Conv3D
    >>> tk.layers.Conv1DTranspose
    >>> tk.layers.Conv2DTranspose
    >>> tk.layers.Conv3DTranspose
    >>> tk.layers.SeparableConv1D
    >>> tk.layers.SeparableConv2D
    >>> tk.layers.DepthwiseConv2D
    """

    transpose: bool
    separable: bool
    depthwise: bool
    filters: int
    kernel_size: t.List[int]

    def conv_class(self, ndim: int) -> t.Type[convolutional.Conv]:
        if self.depthwise:
            if ndim != 4:
                e.code.NotAllowed(
                    msgs=[
                        f"If depthwise convolution it is only available for "
                        f"ndim=2"
                    ]
                )
            if self.separable:
                e.code.NotAllowed(
                    msgs=[
                        f"Separable should be False when using depthwise "
                        f"convolution"
                    ]
                )
            if self.transpose:
                e.code.NotAllowed(
                    msgs=[
                        f"Transpose is not available for depthwise convolution"
                    ]
                )
            return tk.layers.DepthwiseConv2D
        if self.separable:
            if self.transpose:
                e.code.CodingError(
                    msgs=[
                        f"transpose not available for separable conv nets in "
                        f"tensorflow ..."
                    ]
                )
                raise
            if ndim == 3:
                return tk.layers.SeparableConv1D
            elif ndim == 4:
                return tk.layers.SeparableConv2D
            else:
                e.code.CodingError(
                    msgs=[
                        f"3D Separable conv not available in tensorflow ..."
                    ]
                )
                raise
        else:
            if ndim == 3:
                if self.transpose:
                    return tk.layers.Conv1DTranspose
                else:
                    return tk.layers.Conv1D
            elif ndim == 4:
                if self.transpose:
                    return tk.layers.Conv2DTranspose
                else:
                    return tk.layers.Conv2D
            elif ndim == 5:
                if self.transpose:
                    return tk.layers.Conv3DTranspose
                else:
                    return tk.layers.Conv3D
            else:
                e.code.CodingError(
                    msgs=[
                        f"We only recognize shape with 3, 4 or 5 dims",
                        f"Note that we also consider that first dim is for "
                        f"batch_size and also there will be extra dim for "
                        f"channel"
                    ]
                )
                raise

    # noinspection DuplicatedCode
    def build(self, *, inputs: layers.Layer) -> layers.Layer:
        # check
        _ndim = len(inputs.input_shape)

        # estimate conv shape based on inputs shape
        _conv = self.conv_class(ndim=_ndim)

        # build and return
        # noinspection PyArgumentList
        return _conv(
            filters=self.filters,
            kernel_size=self.kernel_size,
            name=self.name,
            data_format=settings.Tf.data_format_k,
        )(inputs)


@dataclasses.dataclass(frozen=True)
class Concat(Block):
    """
    Refer to
    >>> tk.layers.Concatenate
    """
    axis: int

    # noinspection PyMethodOverriding
    def build(
        self, *,
        inputs: t.Union[t.List[layers.Layer], t.Dict[str, layers.Layer]]
    ) -> layers.Layer:
        # ------------------------------------------------------------------01
        # check inputs
        ...

        # ------------------------------------------------------------------02
        # if not list convert list after ordering keys
        if isinstance(inputs, dict):
            _dict_keys = list(inputs.keys())
            _dict_keys.sort()
            inputs = [
                inputs[_k] for _k in _dict_keys
            ]

        # ------------------------------------------------------------------03
        # concat list of layers and return
        return tk.layers.Concatenate(
            axis=self.axis, name=self.name
        )(inputs)
