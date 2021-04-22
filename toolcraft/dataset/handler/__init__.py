"""

Used when you set fields of Dataset class

This package holds logic for handling the values that are set to the field

# todo: explore tf.data.Options for static optimizations
    also check tf.data.experimental.OptimizationOptions

# todo: explore
   + tf.data.TFRecordDataset
   + tf.data.TextLineDataset
   + tf.data.experimental.CsvDataset

# todo: base things on tf.gfile

todo: the value can be converted to value_function so that we can call
 when needed and may be also adapt quickly to create python generators
 or else tensorflow tf.records .... currently when field is used it
 will pile up system memory with numpy arrays

todo: how to handle different shape types may be return enum to tell
   if 1D 2D etc. also have to add more details like time sequences etc
   https://stackoverflow.com/questions/38714959/
   understanding-keras-lstms/50235563#50235563
   
todo: need to integrate tensorflow_datasets
  the pieces of public_api can be reused
  import tensorflow_datasets
  
todo: read about tensorflow.io https://github.com/tensorflow/io any file
  system can be added under this
  https://stackoverflow.com/questions/37304461/tensorflow-importing-data-
  from-a-tensorboard-tfevent-file
  
"""

import enum
import typing as t
import numpy as np
import tensorflow as tf

# this is only for typing support
SUPPORTED_FORMATS = t.Union[
    np.ndarray
]


def tensorify_field(
    field_name: str,
    field_value: t.Union[
        t.Dict[str, SUPPORTED_FORMATS],
        SUPPORTED_FORMATS
    ]
) -> t.Union[t.Dict[str, tf.Tensor], tf.Tensor]:
    """
    generates tensor from blob_field_value and tensor name from
    blob_field_name and dict keys (if blob_field_value is dict)
    Args:
        field_name:
        field_value:

    Returns:

    """
    
    if isinstance(field_value, dict):
        _ret = {}
        for k, v in field_value.items():
            try:
                fmt = SupportedFileFormat.guess_format_from_value(v)
                fmt.validate(v)
                _ret[k] = fmt.convert_to_tensor(
                    name=f"{field_name}.{k}", value=v)
            except Exception as e:
                raise type(e)(
                    f"Failed to filter value for dict item {k!r} of blob "
                    f"field {field_name!r}",
                    *e.args
                )
        return _ret
    else:
        try:
            fmt = SupportedFileFormat.guess_format_from_value(field_value)
            fmt.validate(field_value)
            return fmt.convert_to_tensor(
                name=f"{field_name}", value=field_value)
        except Exception as e:
            raise type(e)(
                f"Failed to filter value for blob field {field_name!r}",
                *e.args
            )


class SupportedFileFormat(enum.Enum):
    NPY = enum.auto()
    
    @property
    def type(self) -> t.Type:
        if self is self.NPY:
            return np.ndarray
        else:
            raise NotImplementedError("NOT SUPPORTED")
    
    @classmethod
    def guess_format_from_value(
            cls,
            value: SUPPORTED_FORMATS,
    ) -> "SupportedFileFormat":
        if isinstance(value, np.ndarray):
            return cls.NPY
        else:
            raise TypeError(
                f"{cls.guess_format_from_value.__name__}: "
                f"Unsupported value {value} with type {type(value)}."
            )
    
    def validate(
            self,
            value: SUPPORTED_FORMATS,
    ):
        
        # more validation logic for future
        # todo: if using file paths can check here if
        #  file exists_with_hash_check and
        #  check its content here. Currently for numpy array no such
        #  check needed :)
        pass
    
    def convert_to_tensor(
            self,
            name: str,
            value: SUPPORTED_FORMATS,
    ) -> tf.Tensor:
        if self is self.NPY:
            # todo: in non-eager method we will have problem, consider using
            #  tf.placeholders
            #  Note that if `tensors` contains a NumPy array, and eager
            #  execution is not enabled, the values will be embedded in the
            #  graph as one or more `tf.constant` operations. For large
            #  datasets (> 1 GB), this can waste memory and run into byte
            #  limits of graph serialization. If `tensors` contains one or
            #  more large NumPy arrays, consider the alternative described in
            #  [this guide](
            #  https://tensorflow.org/guide/datasets#consuming_numpy_arrays).
            #  ... placeholder is not in tf 2.0 so need to look if needed or
            #      else load from *.npz files on the disk
            return tf.convert_to_tensor(value, name=name)
        else:
            raise NotImplementedError(
                f"{self.convert_to_tensor.__name__}: "
                f"Type {self} is not yet supported."
            )


class FileHandler:
    """
    todo:
    In future .... for handling files
    """
    ...
