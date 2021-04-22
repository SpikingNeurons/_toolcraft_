# noinspection GrazieInspection
"""

Good arguments and use cases for functional API
https://medium.com/tensorflow/what-are-symbolic-and-imperative-apis-in-tensorflow-2-0-dfccecb01021

# todo: Understand symbolic vs imperative programming

# https://medium.com/tensorflow/what-are-symbolic-and-imperative-apis-in-tensorflow-2-0-dfccecb01021

# https://mxnet.incubator.apache.org/versions/master/architecture/program_model.html

# https://blog.revolutionanalytics.com/2016/08/deep-learning-part-1.html

# https://gist.github.com/fchollet/1fe9115dff011545a2ad13349bba2ea1

# https://medium.com/tensorflow/what-are-symbolic-and-imperative-apis-in-tensorflow-2-0-dfccecb01021

Example for more complicated functional pipeline:
https://www.tensorflow.org/alpha/guide/keras/functional

sample_weight vs class_weight
https://stackoverflow.com/questions/43459317/keras-class-weight-vs-sample-weights-in-the-fit-generator

# todo: FINISH CRASH COURSE
    https://developers.google.com/machine-learning/crash-course/


effective tf2
https://www.tensorflow.org/guide/effective_tf2

todo: Study these add functions, they can be used to have model layer dependent
  behaviours to do complex things
  + tk.Model.add_weight
      can add a tensor that tracks things like activations, gradients
  + tk.Model.add_metric
  + tk.Model.add_loss
      learn complex losses that depend on multi layers
  + tk.Model.add_update


todo: Explore keras-tuner:
  https://www.tensorflow.org/tutorials/keras/keras_tuner
  Note AutoKeras uses keras tuner but doesnet seem to mature enough
>>> import kerastuner as kt
>>> kt.Hyperband
"""

import dataclasses
import abc
import tensorflow.keras as tk
import tensorflow as tf
import pathlib
import pyarrow as pa
import copy
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np
import sklearn as sk
import typing as t
from tensorflow.python.summary import summary
from tensorflow.keras.layers import Layer
from tensorflow.python.eager import backprop

from .. import logger
from .. import marshalling as m
from .. import dataset
from .. import error as e
from .. import util
from .. import settings
from .. import storage as s
from . import callback
from .callback import logs as lm

_LOGGER = logger.get_logger()

BLOCK_IN_OUT_TYPE = t.Union[Layer, t.List[Layer], t.Dict[str, Layer]]
CHKPT_VARIABLES_TYPE = t.Dict[
    str, t.Union[tf.Variable, tk.Model, tk.optimizers.Optimizer]
]


@dataclasses.dataclass(frozen=True)
class _Checkpoint(s.FileGroup):
    """
    Every tensorflow checkpoint is made up of multiple files starting with
    same name similar to FileGroup. So we prefer to treat a group of
    checkpoint files as single ChkptFile ... so we avoid a name
    TfCheckPointFileGroup.
    """

    parent_folder: "_CheckpointManager"
    epoch: int

    @property
    def is_auto_hash(self) -> bool:
        return True

    @property
    def name(self) -> str:
        """
        We override this property as we want readable name.
        Note that parent_folder can be ignored as file will go in different
        parent folders anyways
        """
        return f"{self.epoch:06d}"

    @property
    @util.CacheResult
    def file_keys(self) -> t.List[str]:
        return [
            "model.data-00000-of-00001", "model.index"
        ]

    @property
    def prefix(self) -> str:
        """
        Return str that is understood by `tf.train.CheckPoint`
        """
        return (self.path / "model").as_posix()

    def print(self):
        """
        Inspired from
        /tensorflow/python/tools/inspect_checkpoint.py
        """
        from tensorflow.python.tools import inspect_checkpoint
        inspect_checkpoint.print_tensors_in_checkpoint_file(
            file_name=self.prefix, tensor_name=None, all_tensors=True
        )

    def create_file(self, *, file_key: str) -> pathlib.Path:
        # get file path
        _file_path = self.path / file_key

        # create if not there note that all files in `self.file_keys` are
        # created here
        if file_key in self.file_keys:
            if file_key == self.file_keys[0]:
                # get smart chkpt
                _smart_chkpt = self.parent_folder.for_hashable.chkpt
                # make sure that current_epoch is same as the checkpoint we
                # are writing
                # Note that the current_epoch anyways reads the value inside
                if _smart_chkpt.epoch != self.epoch:
                    e.code.CodingError(
                        msgs=[
                            f"The checkpoint ins smart chkpt is not in sync "
                            f"with the checkpoint you are writing",
                            {
                                'expected epoch':
                                    self.epoch,
                                'epoch in model.chkpt':
                                    _smart_chkpt.epoch,
                            }
                        ]
                    )
                # the _chkpt.save does more things like increment
                # save_counter also it tries to add extra file checkpoint in
                # the store dir that tracks things ... we do not need this so
                # we use low level write ... note that hence we will
                # _chkpt.read as _chkpt.restore no longer is useful
                # noinspection PyProtectedMember
                _smart_chkpt.tf_chkpt.write(file_prefix=self.prefix)
            else:
                ...
        # should never happen
        else:
            e.code.ShouldNeverHappen(
                msgs=[f"Unrecognized file key {file_key}"]
            )
        # return
        return self.path / file_key

    def get_file(self, file_key: str) -> t.Any:
        e.code.NotSupported(
            msgs=[
                f"Methods `get_files()` or `get_file()` method does not make "
                f"sense for checkpoint files manager.",
                f"Check restore method instead."
            ]
        )
        return {}

    def get_files(
        self, *, file_keys: t.List[str]
    ) -> t.Dict[str, t.Any]:
        e.code.NotSupported(
            msgs=[
                f"Methods `get_files()` or `get_file()` method does not make "
                f"sense for checkpoint files manager.",
                f"Check restore method instead."
            ]
        )
        return {}


@dataclasses.dataclass(frozen=True)
class _CheckpointManager(s.Folder):

    for_hashable: "Model"

    @property
    @util.CacheResult
    def path(self) -> pathlib.Path:
        return self.for_hashable.results_folder.chkpt_path

    @property
    def contains(self) -> t.Type[_Checkpoint]:
        return _Checkpoint


class BlockInternal(m.Internal):
    name: str
    model: "Model"
    is_build_done: bool
    name_scope: tf.name_scope
    inputs: BLOCK_IN_OUT_TYPE
    outputs: BLOCK_IN_OUT_TYPE


@dataclasses.dataclass(frozen=True)
class Block(m.HashableClass, abc.ABC):

    @property
    def name(self) -> str:
        return self.internal.name

    @property
    def inputs(self) -> BLOCK_IN_OUT_TYPE:
        return self.internal.inputs

    @property
    def outputs(self) -> BLOCK_IN_OUT_TYPE:
        return self.internal.outputs

    @property
    def model(self) -> "Model":
        return self.internal.model

    @property
    @util.CacheResult
    def internal(self) -> BlockInternal:
        return BlockInternal(owner=self)

    @property
    def is_built(self) -> bool:
        return self.internal.has(item="is_build_done")

    @property
    def group_by_name(self) -> str:
        e.code.CodingError(
            msgs=[
                f"The name for blocks is auto handled by Model so no need to "
                f"use this property ..."
            ]
        )
        return ""

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hookup build
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.build,
            pre_method=cls.build_pre_runner,
            post_method=cls.build_post_runner,
        )

    def build_pre_runner(self, *, inputs: BLOCK_IN_OUT_TYPE):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            e.code.CodingError(
                msgs=[
                    f"Block {self.group_by_name} is already built ...",
                ]
            )

        # ---------------------------------------------------- 02
        # build with name scope
        # todo: name_scope_v1 vs name_scope_v2 ...
        #  check why v2 takes values kwarg
        self.internal.name_scope = tf.name_scope(name=self.name)
        self.internal.name_scope.__enter__()
        self.internal.inputs = inputs

    @abc.abstractmethod
    def build(self, *, inputs: BLOCK_IN_OUT_TYPE) -> BLOCK_IN_OUT_TYPE:
        ...

    def build_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        # ---------------------------------------------------- 01
        # assign and exit name scope
        self.internal.outputs = hooked_method_return_value
        self.internal.name_scope.__exit__(None, None, None)

        # ---------------------------------------------------- 02
        # set to indicate that build is done
        self.internal.is_build_done = True


@dataclasses.dataclass(frozen=True)
class Head(Block, abc.ABC):

    loss: m.FrozenKeras
    optimizer: m.FrozenKeras

    @property
    @abc.abstractmethod
    def metrics(self) -> t.List[tk.metrics.Metric]:
        ...

    def compile(self, kmodel: tk.Model):
        kmodel.compile(
            optimizer=self.optimizer.get(),
            loss=self.loss.get(),
            metrics=self.metrics
        )


class SmartCheckpoint:
    """
    Note that this is different to `_Checkpoint` which is FileGroup that maps to
    checkpoint's on disk and managed by `_CheckpointManager`.
    """
    # this is for typing support
    tf_chkpt: tf.train.Checkpoint
    kmodel: tk.Model
    model: "Model"
    variables: CHKPT_VARIABLES_TYPE

    @property
    def epoch(self) -> int:
        """
        Note that self.epoch is same tf.Variable which is also present in
        self._tf_chkpt

        indicates which epoch the current restored/created checkpoint is at
        """
        # noinspection PyTypeChecker
        return int(self.variables['epoch'])

    def __init__(self, kmodel: tk.Model, model: "Model"):
        """
        Note that instance of this class will be created in
        >>> Model.build_with_scope

        Also note that there will be only one instance per Model instance and
        weights need to be saved or restored based on the epoch.
        """
        # ---------------------------------------------------- 01
        # at start the epoch will be at zero .... as the instance is created
        # during build and weight are yet to be restored if checkpoints are
        # available on the disk
        _epoch = tf.Variable(
            0, trainable=False, name='epoch', dtype=tf.int32
        )

        # ---------------------------------------------------- 02
        # makes some checks for kmodel
        # noinspection PyProtectedMember
        if not kmodel._is_compiled:
            e.code.CodingError(
                msgs=[
                    f"looks like the kmodel is not compiled"
                ]
            )
        if kmodel.optimizer is None:
            e.code.CodingError(
                msgs=[
                    f"The optimizer is not available in model looks like it "
                    f"was not compiled"
                ]
            )
        if not kmodel.stop_training:
            e.validation.NotAllowed(
                msgs=[
                    f"We expect that kmodel should not in training phase"
                ]
            )

        # ---------------------------------------------------- 03
        # make sure that optimizer has train steps 0
        if kmodel.optimizer.iterations.numpy() != 0:
            e.validation.NotAllowed(
                msgs=[
                    f"The checkpoint was just created and was not restored or "
                    f"trained so we expect optimizer iterations to be at zero"
                ]
            )

        # ---------------------------------------------------- 04
        # make variables for tf_chkpt
        _variables = dict(
            epoch=_epoch,
            kmodel=kmodel,
            optimizer=kmodel.optimizer,
        )
        # store tf_chkpt
        self.tf_chkpt = tf.train.Checkpoint(
            root=None,
            **_variables,
        )
        # store model
        self.model = model
        # store kmodel
        self.kmodel = kmodel
        # store variables
        self.variables = _variables
        # also set this smart checkpoint to internal of model
        model.internal.chkpt = self

    def save(self):
        # check if epoch already present
        if self.epoch in self.model.epochs_on_disk:
            e.code.NotAllowed(
                msgs=[
                    f"Checkpoint for epoch {self.epoch} already exists on the "
                    f"disk so we cannot save the model"
                ]
            )

        # make sure that epoch is always greater than that already present on
        # disk as training will always lead to higher epochs
        if bool(self.model.epochs_on_disk):
            if self.epoch <= max(self.model.epochs_on_disk):
                e.code.NotAllowed(
                    msgs=[
                        f"You cannot create tf_chkpt for epoch {self.epoch} as "
                        f"it is not higher than existing epochs on the disk",
                        f"The epochs on the disk are "
                        f"{self.model.epochs_on_disk}",
                    ]
                )

        # create checkpoint ... this will do multiple things
        # + add itself to manager
        # + create actual tensorflow checkpoint files on the disk
        _Checkpoint(
            epoch=self.epoch,
            parent_folder=self.model.manager
        )

        # test if epoch is now present
        if self.epoch not in self.model.epochs_on_disk:
            e.code.ShouldNeverHappen(
                msgs=[
                    f"You just created checkpoint so it should be now "
                    f"available inside manager ..."
                ]
            )

    def restore_epoch(self, epoch: int):
        # ---------------------------------------------- 01
        # check if epoch available
        if epoch not in self.model.epochs_on_disk:
            e.code.NotAllowed(
                msgs=[
                    f"Cannot restore checkpoint for epoch {epoch} as it is "
                    f"not available on the disk.",
                    f"Available epochs on the disk are "
                    f"{self.model.epochs_on_disk}"
                ]
            )

        # ---------------------------------------------- 02
        # since it is available get respective _Checkpoint
        # noinspection PyTypeChecker
        _chkpt = None  # type: _Checkpoint
        for _ in self.model.manager.items.values():
            if _.epoch == epoch:
                _chkpt = _

        # ---------------------------------------------- 03
        # restore it
        # ---------------------------------------------- 03.01
        # first make sure you need to restore
        if epoch == self.epoch:
            e.code.CodingError(
                msgs=[
                    f"The internal checkpoint is already at epoch "
                    f"{self.epoch} ...",
                    f"So make sure to call restore if it is needed ..."
                ]
            )
        # ---------------------------------------------- 03.02
        # restore
        _status = self.tf_chkpt.read(save_path=_chkpt.prefix)
        # ---------------------------------------------- 03.03
        # check _status
        _status.assert_existing_objects_matched()
        _status.assert_nontrivial_match()
        _status.expect_partial()
        # todo: still this is pending ... how to get optimizer state restored
        #  without compiling ??? ... uncomment below code and try to fix this
        # _status.assert_consumed()
        # ---------------------------------------------- 03.04
        # redundant assert
        e.code.AssertError(
            value1=epoch, value2=self.epoch,
            msgs=[
                f"This was expected to be same",
                dict(found=self.epoch, expected=epoch),
            ]
        )

    def get_weights(self) -> CHKPT_VARIABLES_TYPE:
        _ret = {}
        for k, v in self.variables.items():
            if isinstance(v, tf.Variable):
                _ret[k] = v.value()
            else:
                _ret[k] = v.get_weights()
        return _ret

    def set_weights(self, weights: CHKPT_VARIABLES_TYPE):
        for k, v in weights.items():
            if isinstance(self.variables[k], tf.Variable):
                self.variables[k].assign(v)
            else:
                self.variables[k].set_weights(weights=v)


@dataclasses.dataclass(frozen=True)
class ModelResultsFolder(s.Folder):
    """
    This is the dir under which we will have
    + model image and summary
    + chkpt_manager
    + storage i.e. results from methods with StoreField decorator
    + tensorboard related stuff


    Tensorboard
    todo: summary.FileWriter creates events with no control on name we need
      to add code to clean disk before tensorboard is launched
    todo: We might want to have Tensorboard callback to do things instead of
      this class. As it also supports profiling, embedding, embedding images,
      summary writing and also model graph
    """

    for_hashable: "Model"

    @property
    @util.CacheResult
    def path(self) -> pathlib.Path:
        return settings.Dir.MODEL / \
            self.for_hashable.fit_dataset.group_by_name / \
            self.for_hashable.group_by_name / self.name

    @property
    @util.CacheResult
    def summary_file(self) -> pathlib.Path:
        return self.path / f"model_summary.txt"

    @property
    @util.CacheResult
    def model_image_file(self) -> pathlib.Path:
        return self.path / f"model_image.png"

    @property
    @util.CacheResult
    def chkpt_path(self) -> pathlib.Path:
        return self.path / "chkpt"

    @property
    @util.CacheResult
    def storage_path(self) -> pathlib.Path:
        return self.path / "store"

    @property
    @util.CacheResult
    def tb_path(self) -> pathlib.Path:
        return self.path / "tb"

    def import_model_to_tb(self):
        """
        todo: implement from
          https://www.tensorflow.org/api_docs/python/tf/summary/graph
          Currently in nightly build

        todo: Also try. Based on the code at
          /tensorflow/python/tools/saved_model_utils.py
        """
        _writer = tf.summary.create_file_writer(
            logdir=self.tb_path.as_posix(),
            filename_suffix='model_graph'
        )
        with _writer.as_default():
            ...
        _model_graph_writer = summary.FileWriter(
            self.tb_path.as_posix(),
            graph=self.for_hashable.internal.kmodel_graph,
            filename_suffix='model_graph'
        )
        _model_graph_writer.flush()
        _model_graph_writer.close()

    def launch_tensorboard(self):
        """
        Launches tensorboard in thread
        """
        import threading

        def _launch_tensorboard(folder: pathlib.Path):
            import os
            import webbrowser

            port = util.find_free_port()
            os.system(
                f'tensorboard '
                f'--logdir={folder.resolve().as_posix()} '
                f'--port={port} '
            )

            webbrowser.open_new(url=f"http://localhost:{port}/")

        _thread = threading.Thread(
            target=_launch_tensorboard, args=([self.tb_path, ])
        )
        _thread.start()

    def dump_kmodel_info(self):
        # -------------------------------------------------------------------01
        # some references to file
        _model_summary_text_file = self.summary_file
        _model_image_file = self.model_image_file
        # if all file exists return
        if _model_summary_text_file.is_file() and \
                _model_image_file.is_file():
            return
        else:
            _model_summary_text_file.unlink(missing_ok=True)
            _model_image_file.unlink(missing_ok=True)

        # -------------------------------------------------------------------02
        # get kmodel from checkpoint definition
        _kmodel = self.for_hashable.chkpt.kmodel

        # -------------------------------------------------------------------03
        # save model summary
        _summary_lines = []
        _kmodel.summary(print_fn=lambda _s: _summary_lines.append(_s))
        _model_summary_text_file.write_text("\n".join(_summary_lines))

        # -------------------------------------------------------------------04
        # save model image
        tk.utils.plot_model(
            _kmodel,
            to_file=_model_image_file.as_posix(),
            show_shapes=True,
            show_layer_names=True,
            rankdir='TB',
            expand_nested=True,
            dpi=96
        )


class ModelInternal(m.Internal):
    is_build_done: bool
    chkpt: SmartCheckpoint


@dataclasses.dataclass(frozen=True)
class Model(m.HashableClass, abc.ABC):
    """
    Rationale: always make sure that models are saved based on epochs. And
     when we want more granular saving use `fit_steps_per_epoch` and
     `validate_steps` to update number of steps in epoch and make
     input dataset to loop over infinitely. Also ensure that `save_freq`
     argument to ModelCheckpointEnhanced is 'epoch'.
    """

    # the fit dataset and validate dataset
    fit_dataset: dataset.Dataset
    validate_dataset: dataset.Dataset

    # monitor stuff
    monitor_metric: str
    monitor_min_is_better: bool

    @property
    @util.CacheResult
    def internal(self) -> ModelInternal:
        return ModelInternal(owner=self)

    @property
    @util.CacheResult
    def chkpt(self) -> SmartCheckpoint:
        if not self.is_built:
            e.code.CodingError(
                msgs=[
                    f"SmartCheckpoint is available only after building the "
                    f"model",
                    f"Please call `build_with_scope`"
                ]
            )
        return self.internal.chkpt

    @property
    @util.CacheResult
    def manager(self) -> _CheckpointManager:
        return _CheckpointManager(
            for_hashable=self, parent_folder=None
        )

    @property
    def epochs_on_disk(self) -> t.List[int]:
        return [
            cf.epoch for cf in self.manager.items.values()
        ]

    @property
    def latest_epoch(self) -> t.Optional[int]:
        """
        We have to estimate this based on history stored by model
        """
        _exists = self.storage_train_history(mode='e')
        if _exists:
            _fit_hist = self.storage_train_history(mode='r').to_pandas()
            _epoch = _fit_hist["epoch"].max()
            _ret = int(_epoch)
        else:
            _ret = None
        return _ret

    @property
    def best_epoch(self) -> t.Optional[int]:
        val_exists = self.storage_validate_history(mode='e')
        if val_exists:
            val = self.storage_validate_history(mode='r').to_pandas()
            if self.monitor_min_is_better:
                _best_val = val[self.monitor_metric].min()
            else:
                _best_val = val[self.monitor_metric].max()
            # if multiple epoch matches we pick the minimum
            # (alternative is `.values[0]` which might pick any epoch that
            # matches)
            _ret = val[val[self.monitor_metric] == _best_val]["epoch"].min()
            _ret = int(_ret)
        else:
            # todo: redundant remove later
            fit_exists = self.storage_train_history(mode='e')
            if fit_exists:
                e.code.ShouldNeverHappen(
                    msgs=[
                        f"Validation epoch and fit epoch must be same"
                    ]
                )
            _ret = None
        return _ret

    @property
    def num_classes(self) -> int:
        return self.fit_dataset.num_classes

    @property
    @util.CacheResult
    def group_by_name(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}"

    @property
    def is_built(self) -> bool:
        return self.internal.has(item="is_build_done")

    @property
    @util.CacheResult
    def results_folder(self) -> ModelResultsFolder:
        return ModelResultsFolder(
            for_hashable=self, parent_folder=None
        )

    @property
    @util.CacheResult
    def store_fields_location(self) -> pathlib.Path:
        return self.results_folder.storage_path

    @property
    def is_training(self) -> bool:
        return not self.chkpt.kmodel.stop_training

    @abc.abstractmethod
    def extract_inputs(
        self, data: t.Dict[str, tf.Tensor]
    ) -> t.Union[tf.Tensor, t.Dict[str, tf.Tensor]]:
        """
        The data generated by dataset is a dict of tensors.

        What items from those are input to model is decided by this method.

        In case input is singular return one element else return dict
        """
        ...

    @abc.abstractmethod
    def extract_outputs(
        self, data: t.Dict[str, tf.Tensor]
    ) -> t.Union[None, tf.Tensor, t.Dict[str, tf.Tensor]]:
        """
        The data generated by dataset is a dict of tensors.

        What items from those are output of model is decided by this method.

        In case output is singular return one element else return dict.

        In cases like unsupervised learning return None, as output is
        not needed.
        """
        ...

    @abc.abstractmethod
    def extract_sample_weights(
        self, data: t.Dict[str, tf.Tensor]
    ) -> t.Union[None, tf.Tensor, t.Dict[str, tf.Tensor]]:
        """
        The data generated by dataset is a dict of tensors.

        What items from those are sample_weights of model is decided by this
        method.

        In sample_weight is singular return one element else return dict.

        In case we do not need sample weights return None.

        todo: We might never need to return dict of tensors. If that is the
          case then update return type.
        """
        ...

    def init_validate(self):
        # ------------------------------------------ 01
        # call super
        super().init_validate()

        # ------------------------------------------ 02
        # make sure that if history present then both latest and best epoch
        # chkpt_manager are available
        # ------------------------------------------ 02.01
        _fit_exists = self.storage_train_history(mode='e')
        _validate_exists = self.storage_validate_history(mode='e')
        # noinspection PyUnresolvedReferences
        if _fit_exists ^ _validate_exists:
            e.validation.NotAllowed(
                msgs=[
                    f"Either one of fit or validate history is present. We "
                    f"expect both or None to be present",
                    {
                        '_fit_exists': _fit_exists,
                        '_validate_exists': _validate_exists,
                    }
                ]
            )
        # ------------------------------------------ 02.03
        # if history present test the epochs
        if _fit_exists or _validate_exists:
            _fit_hist = self.storage_train_history(mode='r').to_pandas()
            _fit_epoch = int(_fit_hist["epoch"].max())
            _validate_hist = self.storage_train_history(mode='r').to_pandas()
            _validate_epoch = int(_fit_hist["epoch"].max())
            # -------------------------------------- 02.03.01
            # test if history in sync
            if _fit_epoch != _validate_epoch:
                e.validation.NotAllowed(
                    msgs=[
                        f"The fit and validate history is not in sync",
                        f"Both should be at same epoch",
                        {
                            '_fit_epoch': _fit_epoch,
                            '_validate_epoch': _validate_epoch,
                        }
                    ]
                )
            # -------------------------------------- 02.03.02
            # test if best and latest epoch chkpt_manager on disk
            _epochs_on_disk = self.epochs_on_disk
            _best_epoch, _latest_epoch = self.best_epoch, self.latest_epoch
            if _best_epoch not in _epochs_on_disk:
                e.validation.NotAllowed(
                    msgs=[
                        f"Checkpoint for best epoch {_best_epoch} not "
                        f"available on disk",
                        f"Below are the chkpt_manager on the disk:",
                        _epochs_on_disk
                    ]
                )
            if _latest_epoch not in _epochs_on_disk:
                e.validation.NotAllowed(
                    msgs=[
                        f"Checkpoint for latest epoch {_latest_epoch} not "
                        f"available on disk",
                        f"Below are the chkpt_manager on the disk:",
                        _epochs_on_disk
                    ]
                )
            # -------------------------------------- 02.03.03
            # check if any useless epoch were not deleted
            for _e in _epochs_on_disk:
                if _e not in [_best_epoch, _latest_epoch]:
                    e.code.CodingError(
                        msgs=[
                            f"We are expecting you to call "
                            f"{self.__class__.delete_useless_checkpoints} at "
                            f"end of previous fit epoch to ensure that "
                            f"checkpoints for epochs apart from best and "
                            f"latest epoch are deleted",
                            f"Found checkpoint {_e} on the disk which is not "
                            f"one of {[_best_epoch, _latest_epoch]}"
                        ]
                    )
        # ------------------------------------------ 02.04
        # else if history not present
        else:
            # then test if epochs on disk is empty
            if bool(self.epochs_on_disk):
                e.code.CodingError(
                    msgs=[
                        f"History for model is not present but epoch are "
                        f"present ...",
                        f"Found these epochs on the disk "
                        f"{self.epochs_on_disk}"
                    ]
                )

    def init(self):

        # call super
        super().init()

        # build model
        self.build_with_scope()

        # the validations that we can do only after build is done
        # make sure that kmodel is at epoch 0 and optimizer at step=0
        if self.chkpt.epoch != 0:
            e.code.CodingError(
                msgs=[
                    f"On init we expect the kmodel to be at epoch zero"
                ]
            )
        if self.is_training:
            e.code.CodingError(
                msgs=[
                    f"We expect the internal kmodel not to be in training mode"
                ]
            )
        if self.chkpt.kmodel.optimizer.iterations.numpy() != 0:
            e.code.CodingError(
                msgs=[
                    f"We were expecting the internal optimizer of kmodel to "
                    f"be at iterations zero"
                ]
            )

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hookup build
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.build_with_scope,
            pre_method=cls.build_pre_runner,
            post_method=cls.build_post_runner,
        )

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            e.code.CodingError(
                msgs=[
                    f"Block {self.group_by_name} is already built ...",
                ]
            )

        # ---------------------------------------------------- 02
        # set reference to self i.e. model in all blocks
        # also set a name for them
        for f_name in self.dataclass_field_names:
            value = getattr(self, f_name)
            # if block
            if isinstance(value, Block):
                value.internal.model = self
                value.internal.name = f_name
            # if list of blocks
            if isinstance(value, list):
                _items_that_are_blocks = [
                    isinstance(_, Block) for _ in value
                ]
                _anything_is_block = any(_items_that_are_blocks)
                if any(_items_that_are_blocks):
                    # if anything is Block then everything should be Block
                    if not all(_items_that_are_blocks):
                        e.code.NotAllowed(
                            msgs=[
                                f"If anything in list is a block then "
                                f"everything in list should be a block ...",
                                f"Check field {f_name}"
                            ]
                        )
                    # set model and name for the list of blocks
                    _b: Block
                    for _i, _b in enumerate(value):
                        _b.internal.model = self
                        _b.internal.name = f"{f_name}_{_i}"

        # ---------------------------------------------------- 03
        # Responsible to build all blocks, plus does things like
        # + builds blocks
        # + compile kmodel

    def build_with_scope(self):
        """
        Responsible to build all blocks, plus does things like
        + builds blocks
        + compile kmodel
        """
        # all keras inputs
        _all_keras_inputs = self.fit_dataset.get_keras_inputs()

        # extract input
        _inputs = self.extract_inputs(_all_keras_inputs)

        # extract sample_weights
        # todo: not sure where we need to pass sample weights
        # _sample_weights = self.extract_sample_weights(_all_keras_inputs)

        # build head and hence kmodel
        _head = self.build(_inputs)
        _kmodel = tk.Model(inputs=_inputs, outputs=_head.outputs)

        # the optimizer will be available once we compile kmodel
        _head.compile(kmodel=_kmodel)

        # set this to false
        _kmodel.stop_training = True

        # make a checkpoint with reference to kmodel and self
        # note that self.internal.chkpt will automatically set to internal.chkpt
        SmartCheckpoint(kmodel=_kmodel, model=self)

    @abc.abstractmethod
    def build(self, inputs: t.Union[tf.Tensor, t.Dict[str, tf.Tensor]]) -> Head:
        ...

    # noinspection PyUnusedLocal
    def build_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        # set to indicate that build is done
        self.internal.is_build_done = True

        # stop training in kmodel
        self.chkpt.kmodel.stop_training = True

        # since model is build by now we can dump the info
        self.results_folder.dump_kmodel_info()

    def restore_to_best_epoch(self):
        _best_epoch = self.best_epoch
        if _best_epoch is not None:
            self.chkpt.restore_epoch(epoch=self.best_epoch)

    def restore_to_latest_epoch(self):
        _latest_epoch = self.latest_epoch
        if _latest_epoch is not None:
            self.chkpt.restore_epoch(epoch=self.latest_epoch)

    def save(self):
        self.chkpt.save()

    def delete_useless_checkpoints(self):
        """
        Here we try to delete checkpoints on the disk that are not latest
        and not the best to save disk space.

        This is completely dependent on history and the monitoring metric
        """
        # get checkpoints that are eligible to delete
        _chkpts_to_delete = []  # type: t.List[_Checkpoint]
        _latest_nd_best_epoch = [self.latest_epoch, self.best_epoch]
        for _chkpt in self.manager.items.values():
            if _chkpt.epoch not in _latest_nd_best_epoch:
                _chkpts_to_delete.append(_chkpt)

        # delete checkpoints
        for _chkpt in _chkpts_to_delete:
            _chkpt.delete(force=True)

        # make sure that epochs on the disk is updated
        for _chkpt in self.manager.items.values():
            if _chkpt.epoch not in _latest_nd_best_epoch:
                e.code.CodingError(
                    msgs=[
                        f"We were expecting that checkpoint for epoch "
                        f"{_chkpt.epoch} is deleted by now ..."
                    ]
                )

    # noinspection PyUnusedLocal
    @s.StoreField(partition_cols=['epoch'])
    def storage_train_history(
            self, mode: s.MODE_TYPE, epoch: int, data: t.Dict
    ) -> pa.Table:
        return pa.table(
            data={
                'epoch': [epoch],
                **data,
            }
        )

    # noinspection PyUnusedLocal
    @s.StoreField(partition_cols=['epoch'])
    def storage_validate_history(
            self, mode: s.MODE_TYPE, epoch: int, data: t.Dict
    ) -> pa.Table:
        return pa.table(
            data={
                'epoch': [epoch],
                **data,
            }
        )

    # noinspection PyUnusedLocal
    @s.StoreField(partition_cols=['epoch'])
    def storage_classification_stats(
        self, mode: s.MODE_TYPE, epoch: int
    ) -> pa.Table:
        # --------------------------------------------------------- 01
        # check if model is restored to `epoch`
        if epoch != self.chkpt.epoch:
            e.validation.NotAllowed(
                msgs=[
                    f"Please restore the model to epoch {epoch}.",
                    f"Currently it is pointing to epoch {self.chkpt.epoch}."
                ]
            )

        # --------------------------------------------------------- 02
        # some variables
        _validate_dataset = self.validate_dataset

        # --------------------------------------------------------- 03
        # compute
        with logger.Spinner(
                title=f"Computing classification statistics for epoch {epoch}",
                logger=_LOGGER
        ) as spinner:
            # ----------------------------------------------------- 03.01
            # construct _y_true and _y_pred
            spinner.text = "extracting predictions"
            _y_true = []
            _y_pred = []
            for _batch in _validate_dataset(as_numpy=True):
                _preds = self.predict_step(_batch).numpy().argmax(axis=1)
                _labels = _batch.y_true
                _y_true.append(_labels)
                _y_pred.append(_preds)
            _y_true = np.hstack(_y_true)
            _y_pred = np.hstack(_y_pred)

            # ----------------------------------------------------- 03.01
            # compute stats
            spinner.text = "computing statistics"
            _stats = sk.metrics.classification_report(
                y_true=_y_true, y_pred=_y_pred,
                output_dict=True, zero_division=0
            )
            spinner.text = "computing confusion matrix"
            _cm = sk.metrics.confusion_matrix(
                y_true=_y_true, y_pred=_y_pred,
            )

        # --------------------------------------------------------- 04
        # data to store
        _store_data = {
            'label': [],
            'predicted for times': [],
            'precision': [],
            'recall': [],
            'f1-score': [],
            'support': [],
            'confusion_matrix': [],
        }
        # --------------------------------------------------------- 04.01
        # for class labels
        for _l in range(_validate_dataset.num_classes):
            # add label
            _store_data['label'].append(f"{_l:03d}")
            # add standard stats
            for cn in ['precision', 'recall', 'f1-score', 'support']:
                _store_data[cn].append(_stats[str(_l)][cn])
            # add confusion matrix related stats
            _store_data['confusion_matrix'].append(_cm[_l])
            # add 'predicted for times'
            _store_data['predicted for times'].append(
                (_y_pred == _l).sum()
            )

        # --------------------------------------------------------- 04.02
        # for avg stats
        for _l in ['macro avg', 'weighted avg']:
            # add label
            _store_data['label'].append(_l)
            # add standard stats
            for cn in ['precision', 'recall', 'f1-score', 'support']:
                _store_data[cn].append(_stats[_l][cn])
            # add confusion matrix related stats
            _store_data['confusion_matrix'].append([])
            # add 'predicted for times'
            _store_data['predicted for times'].append(
                len(_y_pred)
            )

        # --------------------------------------------------------- 05
        return pa.table(
            data={
                'epoch': [epoch] * len(_store_data['label']),
                **_store_data,
            }
        )

    def fit_train_epoch(
        self,
        batch_size: int,
        cbs_manager: callback.CallbacksManager,
    ) -> t.Dict:
        # ----------------------------------------------------- f 01
        # reset metrics for fit phase
        self.chkpt.kmodel.reset_metrics()
        # ----------------------------------------------------- f 02
        # fit start
        cbs_manager.on_train_start(
            logs=lm.PhaseStartLogs()
        )
        # ----------------------------------------------------- f 03
        # fit batch loop
        for batch_id, batch in enumerate(
            self.fit_dataset(
                as_ktuple=False,
                as_numpy=False,
                normalize=True,
                batch_size=batch_size,
            )
        ):
            # ------------------------------------------------- f 03.01
            # fit batch start
            cbs_manager.on_train_batch_start(
                batch=batch_id,
                logs=lm.BatchStartLogs(
                    batch=batch_id,
                )
            )
            # ------------------------------------------------- f 03.02
            # fit step
            fit_step_res = self.train_step(data=batch)
            # ------------------------------------------------- f 03.03
            # fit batch end
            cbs_manager.on_train_batch_end(
                batch=batch_id,
                logs=lm.BatchEndLogs(
                    batch_results=fit_step_res,
                )
            )
        # ----------------------------------------------------- f 04
        # fit epoch results
        # noinspection PyUnboundLocalVariable
        fit_epoch_res = copy.copy(fit_step_res)
        # ----------------------------------------------------- f 05
        # fit end
        cbs_manager.on_train_end(
            logs=lm.PhaseEndLogs()
        )
        # ----------------------------------------------------- f 06
        return fit_epoch_res

    def fit_validate_epoch(
        self,
        batch_size: int,
        cbs_manager: callback.CallbacksManager,
    ) -> t.Dict:
        # ----------------------------------------------------- v 01
        # reset metrics for fit phase
        self.chkpt.kmodel.reset_metrics()
        # ----------------------------------------------------- v 02
        # validate start
        cbs_manager.on_validate_start(
            logs=lm.PhaseStartLogs()
        )
        # ----------------------------------------------------- v 03
        # validate batch loop
        for batch_id, batch in enumerate(
            self.validate_dataset(
                as_ktuple=False,
                as_numpy=False,
                normalize=True,
                batch_size=batch_size,
            )
        ):
            # ------------------------------------------------- v 03.01
            # validate batch start
            cbs_manager.on_validate_batch_start(
                batch=batch_id,
                logs=lm.BatchStartLogs(
                    batch=batch_id,
                )
            )
            # ------------------------------------------------- v 03.02
            # validate step
            validate_step_res = self.validate_step(
                data=batch
            )
            # ------------------------------------------------- v 03.03
            # validate batch end
            cbs_manager.on_validate_batch_end(
                batch=batch_id,
                logs=lm.BatchEndLogs(
                    batch_results=validate_step_res,
                )
            )
        # ----------------------------------------------------- f 04
        # validate epoch results
        # noinspection PyUnboundLocalVariable
        validate_epoch_res = copy.copy(validate_step_res)
        # ----------------------------------------------------- v 05
        # validate end
        cbs_manager.on_validate_end(
            logs=lm.PhaseEndLogs()
        )
        # ----------------------------------------------------- v 06
        return validate_epoch_res

    def fit(
        self,
        batch_size: int,
        exit_after_secs: int,
        callbacks: t.List[
            t.Union[callback.Callback, callback.ParallelCallback]
        ] = None,
        early_stopping_patience: t.Optional[int] = 3,
        until_epoch: t.Optional[int] = None,
        validate_after_fit_epochs: int = 1,
    ):
        # --------------------------------------------------------- 01
        # check if model was build
        if not self.is_built:
            e.code.CodingError(
                msgs=[
                    f"You are supposed to build the model before calling fit "
                    f"..."
                ]
            )
        # if stop early exit :)
        if self.stop_early(early_stopping_patience):
            _LOGGER.info(
                msg=f"Converged so stopping early "
                    f"with best epoch {self.best_epoch}")
            return
        # if until an epoch reached exit ...
        if until_epoch is not None:
            _latest_epoch = self.latest_epoch
            if _latest_epoch is not None:
                if _latest_epoch >= until_epoch:
                    _LOGGER.info(
                        msg=f"Reached maximum epoch limit of {until_epoch}")
                    return

        # --------------------------------------------------------- 02
        # add a callback for `exit_after_secs`
        # we do it here as exit_after_secs kwarg is available only after fit
        # is called
        if callbacks is None:
            callbacks = []
        callbacks += [callback.ExitFitAfterSecs(secs=exit_after_secs)]

        # --------------------------------------------------------- 03
        # create a manager for callbacks
        # this will also validate callbacks used for fit
        _cbs_manager = callback.CallbacksManager(
            callbacks=callbacks, model=self,
        )

        # --------------------------------------------------------- 04
        # estimate initial epoch and enable kmodel for training
        # --------------------------------------------------------- 04.01
        # set initial epoch
        _initial_epoch = self.latest_epoch
        if _initial_epoch is None:
            # set it to zero
            _initial_epoch = 0
            # make sure that checkpoint is at epoch zero
            e.code.AssertError(
                value1=self.chkpt.epoch, value2=0,
                msgs=[
                    f"We expect the checkpoint to be at epoch zero ..."
                ]
            )
            # todo: remove later
            assert self.chkpt.epoch == 0, "We expect this to be zero"
        else:
            # restore weights as latest epoch is available .... and hence
            # resume training ...
            if self.chkpt.epoch == 0:
                self.restore_to_latest_epoch()
            else:
                if self.chkpt.epoch != _initial_epoch:
                    e.code.CodingError(
                        msgs=[
                            f"If chkpt is not at epoch zero then that does "
                            f"mean that it should be at latest epoch as we "
                            f"assume that you will be resuming the training "
                            f"from last call to fit ..."
                        ]
                    )
        # --------------------------------------------------------- 04.02
        # set stop_training to False
        # noinspection PyProtectedMember
        _kmodel = self.chkpt.kmodel
        if not _kmodel.stop_training:
            e.code.CodingError(
                msgs=[
                    f"Make sure that kmodel is not enabled for training "
                    f"before calling fit.",
                    f"Check if after build and compile for kmodel the "
                    f"stop_training is set to True"
                ]
            )
        _kmodel.stop_training = False

        # --------------------------------------------------------- 05
        # the lifecycle of fit
        # --------------------------------------------------------- 05.01
        # enter fit
        _cbs_manager.on_fit_enter()
        # --------------------------------------------------------- 05.02
        # loop infinitely for epochs until `stop_training` is set to True
        # Note: `callback.ExitFitAfterSecs` will take care of setting,
        #   stop_training to True, so that infinite loop can exit
        _current_epoch = _initial_epoch
        while not _kmodel.stop_training:
            # ----------------------------------------------------- 05.02.01
            # increment current epoch
            _current_epoch += 1
            # ----------------------------------------------------- 05.02.02
            # epoch start
            _cbs_manager.on_epoch_start(
                epoch=_current_epoch,
                logs=lm.EpochStartLogs()
            )
            # ----------------------------------------------------- 05.02.03
            # fit phase
            _fit_epoch_res = self.fit_train_epoch(
                cbs_manager=_cbs_manager, batch_size=batch_size,
            )
            # ----------------------------------------------------- 05.02.04
            # validate phase ... do only if needed ...
            # i.e. when _current_epoch in multiple of validate_after_fit_epochs
            _validate_epoch_res = None
            if _current_epoch % validate_after_fit_epochs == 0:
                _validate_epoch_res = self.fit_validate_epoch(
                    cbs_manager=_cbs_manager, batch_size=batch_size,
                )
            # ----------------------------------------------------- 05.02.05
            # epoch end
            # Note that only after getting results for fit and validate we
            # write results to disk ... so that things are consistent ...
            # also model if best is saved here with help of callback
            _cbs_manager.on_epoch_end(
                epoch=_current_epoch,
                logs=lm.EpochEndLogs(
                    fit_results=_fit_epoch_res,
                    validate_results=_validate_epoch_res,
                )
            )
            # ----------------------------------------------------- 05.02.06
            # if we have converged time to stop training
            if self.stop_early(early_stopping_patience):
                # this will break the current while loop
                _kmodel.stop_training = True
                _LOGGER.info(
                    msg=f"Converged so stopping early "
                        f"with best epoch {self.best_epoch}"
                )
            # if until an epoch is reached then time to stop training
            if until_epoch is not None:
                if _current_epoch >= until_epoch:
                    # this will break the current while loop
                    _kmodel.stop_training = True
                    _LOGGER.info(
                        msg=f"Reached maximum epoch limit of {until_epoch}"
                    )
        # --------------------------------------------------------- 05.03
        # exit fit
        _cbs_manager.on_fit_exit()

    # @tf.function
    def train_step(self, data: t.Dict[str, tf.Tensor]) -> t.Dict:
        """
        todo: need to see if we should override `tk.Model.train_step` to take
          advantage of optimizations made by `tk.Model.make_train_function`
        >>> tk.Model.make_train_function

        The logic for one training step.

        Refer below method for inspiration
        >>> tk.Model.train_step

        Returns:
          A `dict` containing values that will be passed to
          `cbs_manager.on_train_batch_end`. Typically, the
          values of the `Model`'s metrics are returned. Example:
          `{'loss': 0.2, 'accuracy': 0.7}`.
        """
        # -------------------------------------------------------------- 01
        # extract input and output and get model
        _input = self.extract_inputs(data=data)
        _output = self.extract_outputs(data=data)
        _sample_weights = self.extract_sample_weights(data=data)
        # noinspection PyProtectedMember
        _kmodel = self.chkpt.kmodel

        # -------------------------------------------------------------- 02
        # train step from keras ... in case of different logic needed this
        # method needs to be overridden
        with backprop.GradientTape() as tape:
            y_pred = _kmodel(_input, training=True)
            loss = _kmodel.compiled_loss(
                _output, y_pred, _sample_weights,
                regularization_losses=_kmodel.losses
            )
        _kmodel.optimizer.minimize(loss, _kmodel.trainable_variables, tape=tape)
        _kmodel.compiled_metrics.update_state(_output, y_pred, _sample_weights)

        # -------------------------------------------------------------- 03
        # return
        return {_m.name: _m.result().numpy() for _m in _kmodel.metrics}

    # @tf.function
    def validate_step(self, data: t.Dict[str, tf.Tensor]) -> t.Dict:
        """
        todo: need to see if we should override `tk.Model.test_step` to take
          advantage of optimizations made by `tk.Model.make_test_function`
        >>> tk.Model.make_test_function

        The logic for one validation step. (Note that keras calls it test)

        Refer below method for inspiration
        >>> tk.Model.test_step

        Returns:
          A `dict` containing values that will be passed to
          `cbs_manager.on_validate_batch_end`. Typically, the
          values of the `Model`'s metrics are returned.
        """
        # -------------------------------------------------------------- 01
        # extract input and output and get model
        _input = self.extract_inputs(data=data)
        _output = self.extract_outputs(data=data)
        _sample_weights = self.extract_sample_weights(data=data)
        # noinspection PyProtectedMember
        _kmodel = self.chkpt.kmodel

        # -------------------------------------------------------------- 02
        y_pred = _kmodel(_input, training=False)
        # Updates stateful loss metrics.
        _kmodel.compiled_loss(
            _output, y_pred, _sample_weights,
            regularization_losses=_kmodel.losses
        )
        _kmodel.compiled_metrics.update_state(_output, y_pred, _sample_weights)

        # -------------------------------------------------------------- 03
        return {_m.name: _m.result().numpy() for _m in _kmodel.metrics}

    # @tf.function
    def predict_step(
        self, data: t.Dict[str, tf.Tensor]
    ) -> t.Union[tf.Tensor, t.Dict[str, tf.Tensor]]:

        """
        todo: need to see if we should override `tk.Model.predict_step` to take
          advantage of optimizations made by `tk.Model.make_predict_function`
        >>> tk.Model.make_predict_function

        The logic for one predict step.

        Refer below method for inspiration
        >>> tk.Model.predict_step

        Returns:
            The result of one inference step, typically the output of calling
            the `Model` on data.
        """
        # -------------------------------------------------------------- 01
        # extract input and output and get model
        _input = self.extract_inputs(data=data)
        # _output = self.extract_outputs(data=data)
        # _sample_weights = self.extract_sample_weights(data=data)
        _kmodel = self.chkpt.kmodel

        # -------------------------------------------------------------- 02
        # return
        return _kmodel(inputs=_input, training=False)

    def stop_early(self, early_stopping_patience: t.Optional[int]) -> bool:
        # if None never stop early
        if early_stopping_patience is None:
            return False
        # get latest epoch
        _latest_epoch = self.latest_epoch
        # get best epoch
        _best_epoch = self.best_epoch
        # if there was no training no need to stop
        if _latest_epoch is None:
            if _best_epoch is not None:
                e.code.ShouldNeverHappen(
                    msgs=[f"Best epoch should be None if latest epoch is None"]
                )
            return False
        if _best_epoch is None:
            e.code.ShouldNeverHappen(
                msgs=[f"If latest epoch is available then best epoch should "
                      f"also be available"]
            )
        # how many patience epochs are over
        _patience_epochs = _latest_epoch - _best_epoch
        # check is patience epochs have grown too much .... then there is a
        # coding bug
        if _patience_epochs > early_stopping_patience:
            e.code.ShouldNeverHappen(
                msgs=[
                    f"We were not expecting that "
                    f"{_patience_epochs} > "
                    f"{early_stopping_patience}"
                ]
            )
        # return
        return _patience_epochs == early_stopping_patience

    def _get_metrics_fig(self, metric: str):
        _metric = metric
        _epoch = "epoch"
        _legend = "Legend"

        _fit_history = \
            self.storage_train_history(mode='r').to_pandas()
        _validate_history = \
            self.storage_validate_history(mode='r').to_pandas()

        #
        _fit_df = pd.DataFrame()
        _fit_df[_epoch] = _fit_history[_epoch]
        _fit_df[_metric] = _fit_history[_metric]
        _fit_df[_legend] = "fit"
        _fit_df = _fit_df.sort_values(by=[_epoch])

        #
        _validate_df = pd.DataFrame()
        _validate_df[_epoch] = _validate_history[_epoch]
        _validate_df[_metric] = _validate_history[_metric]
        _validate_df[_legend] = "validate"
        _validate_df = _validate_df.sort_values(by=[_epoch])

        #
        _df = pd.concat([_fit_df, _validate_df], ignore_index=True)

        #
        fig = px.line(
            _df, x=_epoch, y=_metric, color=_legend,
            title=f"Metric `{_metric}`",
            range_y=[0., 1.] if _metric == "categorical_accuracy" else None,
        )

        #
        if _metric == "categorical_accuracy":
            _random_guess = "random guess"
            _random_guess_df = pd.DataFrame()
            _random_guess_df[_epoch] = _fit_history[_epoch]
            _random_guess_df[_random_guess] = \
                self.fit_dataset.random_guessing_accuracy
            fig.add_trace(
                go.Scatter(
                    x=_random_guess_df[_epoch],
                    y=_random_guess_df[_random_guess],
                    name=_random_guess,
                    line=dict(color='green', width=2, dash='dash')
                )
            )

        #
        return fig

    def plot_acc(self, return_fig: bool = False):

        #
        fig = self._get_metrics_fig(metric="categorical_accuracy")

        #
        if return_fig:
            return fig
        else:
            fig.show(enderer="browser")

    def plot_loss(self, return_fig: bool = False):

        #
        fig = self._get_metrics_fig(metric="loss")

        #
        if return_fig:
            return fig
        else:
            fig.show(enderer="browser")

    def plot_classifier_stats(
            self, epoch: int, return_fig: bool = False
    ):
        # -------------------------------------------------------- 01
        # get the stats
        _stats = self.storage_classification_stats(
            mode='rw', epoch=epoch).to_pydict()

        # -------------------------------------------------------- 02
        # Confusion Matrix
        # -------------------------------------------------------- 02.01
        # make confusion matrix figure
        _cm_npy = np.asarray(_stats['confusion_matrix'][:-2])
        _cm_fig = px.imshow(
            title=f'Confusion Matrix - Normal (epoch={epoch})',
            img=_cm_npy,
            labels=dict(
                x='Predicted labels', y='True labels', color='Predictions'),
            x=_stats['label'][:-2],
            y=_stats['label'][:-2],
        )
        _cm_fig.update_xaxes(side="top")
        # -------------------------------------------------------- 02.02
        # make confusion matrix figure with contrast
        _cm_contrast_npy = (_cm_npy != 0).astype(np.int)
        _cm_fig_contrast = px.imshow(
            title=f'Confusion Matrix - With Contrast (epoch={epoch})',
            img=_cm_contrast_npy,
            labels=dict(
                x='Predicted labels', y='True labels', color='Predictions'),
            x=_stats['label'][:-2],
            y=_stats['label'][:-2],
        )
        _cm_fig_contrast.update_xaxes(side="top")

        # -------------------------------------------------------- 03
        # compute sort indices
        _sort_by_predicted_for_times_indices = np.argsort(
            _stats['predicted for times'][:-2]
        )[::-1]

        # -------------------------------------------------------- 04
        # stats and stats avg table
        _stats_cols = [
            k for k in _stats.keys() if k not in ['confusion_matrix', 'epoch']
        ]
        _stats_table = go.Table(
            header=dict(
                values=_stats_cols,
                # font=dict(size=10),
                align="center",
            ),
            cells=dict(
                values=[
                    [
                        round(_stats[c][si], 3)
                        if isinstance(_stats[c][si], float)
                        else _stats[c][si]
                        for si in _sort_by_predicted_for_times_indices
                    ]
                    for c in _stats_cols
                ],
                align="center"
            )
        )
        _stats_avg_table = go.Table(
            header=dict(
                values=_stats_cols,
                # font=dict(size=10),
                align="center",
            ),
            cells=dict(
                values=[
                    [
                        round(v, 3) if isinstance(v, float) else v
                        for v in _stats[c][-2:]
                    ]
                    for c in _stats_cols
                ],
                align="center")
        )
        # make subplots
        _all_stats_table = make_subplots(
            rows=2, cols=1,
            # shared_xaxes=True,
            vertical_spacing=0.03,
            specs=[[{"type": "table"}],
                   [{"type": "table"}]]
        )
        _all_stats_table.add_trace(_stats_table, row=1, col=1)
        _all_stats_table.add_trace(_stats_avg_table, row=2, col=1)
        _all_stats_table.update_layout(
            # height=800,
            # showlegend=False,
            title_text=f'Classifier statistics (epoch={epoch})',
        )

        # -------------------------------------------------------- 05
        # return fig
        if return_fig:
            return _cm_fig, _cm_fig_contrast, _all_stats_table
        else:
            _cm_fig.show(enderer="browser")
            _cm_fig_contrast.show(enderer="browser")
            _all_stats_table.show(enderer="browser")
