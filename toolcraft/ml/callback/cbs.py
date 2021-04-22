"""
Saving Model:

1]
Need to modify ModelCheckpoint to save also the remaining callbacks when
model is saved so that training can be resumed. Also create TrainingStopped
callback so that when we try to resume training the pickled TrainingStopped
callback can allow us to exit in Model.fit (not KModel.fit).
https://towardsdatascience.com/resuming-a-training-process-with-keras-3e93152ee11a

2]
The alternative can be make our Model class compatible to run and resume
training use the save decorators. But this will remove the need for
ModelCheckpoint and EarlyStopping callback and we need to have that features
in Model class.

"""

import tensorflow.keras as tk
import dataclasses
import datetime
import pathlib

from ... import error as e
from ... import settings
from ... import logger
from .__base__ import Callback
from . import logs as lm

_LOGGER = logger.get_logger()


# noinspection PyUnreachableCode
if False:
    from ..__base__ import SmartCheckpoint


@dataclasses.dataclass
class Tensorboard(Callback):
    """
    todo: Support this call back there is lot to do here ...
      with this we can support many things
      + model graph visualization (as graph will be available)
      + profiling (check kwarg profile_batch)
      + summary writer
      + embeddings
      + dumping images for embeddings
    >>> tk.callbacks.TensorBoard

    """
    ...


@dataclasses.dataclass
class ExitFitAfterSecs(Callback):
    secs: int
    start_time: datetime.datetime = dataclasses.field(init=False)
    
    def init(self):
        # call super
        super().init()
        
        # assign start time
        # noinspection PyTypeChecker
        self.start_time = None
    
    def init_validate(self):
        # call super
        super().init_validate()
        
        # check if exit_after_secs is positive
        if self.secs <= 0:
            e.validation.NotAllowed(
                msgs=[
                    f"We need exit_after_secs to be greater than zero. "
                    f"Instead, found {self.secs}"
                ]
            )
            
    def on_fit_enter(self):
        # wipe it in case model.fit is called multiple times
        # noinspection PyTypeChecker
        self.start_time = None
        
    def on_epoch_start(
        self, epoch: int, logs: lm.EpochStartLogs
    ):
        # when on_fit_enter this will be wiped ..., so we set it again when
        # first epoch for current fit cycle is triggered
        if self.start_time is None:
            self.start_time = datetime.datetime.now()
        
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs = None
    ):
        _now = datetime.datetime.now()
        _elapsed_secs = (_now - self.start_time).total_seconds()
        _will_exit = _elapsed_secs > self.secs
        self.manager.model.chkpt.kmodel.stop_training = _will_exit


@dataclasses.dataclass
class StopTrainingSemaphore(Callback):
    """
    todo: Update this to track ctrl+C event ...
      check `try_ctrl_c.py`
    """
    
    file: pathlib.Path = \
        settings.Dir.ROOT_DEL / "__delete_me_to_kill_training__"
    
    def on_fit_enter(self):
        # when fit phase starts always create semaphore file
        if not self.file.is_file():
            self.file.touch()
            
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs
    ):
        # to avoid printing multiple times
        if not self.manager.model.is_training:
            return
        # if user has deleted the file then indicate fit phase to stop training
        if not self.file.is_file():
            self.manager.model.chkpt.kmodel.stop_training = True
            _LOGGER.info(
                msg=f"Force stopping the training loop as you deleted the "
                    f"semaphore file ..."
            )
            
    def on_fit_exit(self):
        # if in case we are exiting normally the file will be still there so
        # delete it
        if self.file.is_file():
            self.file.unlink()


@dataclasses.dataclass
class History(Callback):
    """
    Does below things:

    """
    
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs = None
    ):
        epoch = int(epoch)
        self.manager.model.storage_train_history(
            mode='w',
            epoch=epoch,
            data={
                "time": [datetime.datetime.now()],
                **{
                    k: [v]
                    for k, v in logs.fit_results.items()
                }
            }
        )

        # sometimes validation is not done per epoch so this check
        if logs.validate_results is not None:
            self.manager.model.storage_validate_history(
                mode='w',
                epoch=epoch,
                data={
                    "time": [datetime.datetime.now()],
                    **{
                        k: [v]
                        for k, v in logs.validate_results.items()
                    }
                }
            )


@dataclasses.dataclass
class ModelCheckpoint(Callback):
    """
    Note that this callback save the best checkpoint and the last checkpoint
    so that training can be resumed.
    This feature is not available with standard keras library.
    
    This callback is inspired by tk.callbacks.ModelCheckpoint with the
    limitation that it is not adapted for multi-worker setup.
    todo: explore multi-worker setup

    This class do below things:
    + full control on saving model i.e. all options of model.save can be used
    + checkpoint management via storage.tf_chkpt i.e. all hashing and access
      time-stamps
    + support for callback state restore ...
      https://towardsdatascience.com/resuming-a-training-process-with-keras-3e93152ee11a
      todo: caveat - if callbacks are changed when resuming training the code
        is not tested and we have yet not supported raising error. Proceed
        with CAUTION
    + In collaboration with HistoryEnhanced callback here we do early stopping


    Modified ModelCheckpoint to save also the remaining callbacks when
    model is saved so that training can be resumed. Also create TrainingStopped
    callback so that when we try to resume training the pickled TrainingStopped
    callback can allow us to exit in Model.fit (not KModel.fit).


    Rationale: always make sure that models are saved based on epochs. And
     when we want more granular saving use `fit_steps_per_epoch` and
     `validate_steps` to update number of steps in epoch and make
     input dataset to loop over infinitely. Also ensure that `save_freq`
     argument to ModelCheckpointEnhanced is 'epoch'.
     
     >>> tk.callbacks.ModelCheckpoint
     >>> tk.callbacks.EarlyStopping
    """
    class InMemoryChkpt:
        
        def __init__(self, epoch: int, smart_chkpt: "SmartCheckpoint"):
            
            # check if epochs completed are same as supplied epoch
            if epoch != smart_chkpt.epoch:
                e.code.CodingError(
                    msgs=[
                        f"The supplied epochs should match epochs derived from "
                        f"smart chkpt"
                    ]
                )
                
            # save things from kmodel
            self.epoch = epoch
            self.weights = smart_chkpt.get_weights()
            self.smart_chkpt = smart_chkpt
        
        def restore(self):
            _chkpt = self.smart_chkpt
            _chkpt.set_weights(weights=self.weights)
            if self.epoch != _chkpt.epoch:
                e.code.ShouldNeverHappen(msgs=[])

    # noinspection PyTypeChecker,PyAttributeOutsideInit
    def init(self):
        self.best: ModelCheckpoint.InMemoryChkpt = None
        self.latest: ModelCheckpoint.InMemoryChkpt = None
        
    def on_fit_enter(self):

        # ------------------------------------------------------------01
        # get latest and best epoch
        _latest_epoch = self.manager.model.latest_epoch
        _best_epoch = self.manager.model.best_epoch

        # ------------------------------------------------------------02
        # if latest and best epoch not on disk then check that kmodel is not
        # trained for any batches
        if _latest_epoch is None:
            if _best_epoch is not None:
                e.code.ShouldNeverHappen(msgs=[f"Both latest and best epoch "
                                               f"must be None"])
        # ------------------------------------------------------------03
        # if latest and best epoch chkpt_manager are available then:
        # + confirm if kmodel is at latest epoch
        # + back up latest epoch weights in memory
        # + restore kmodel with best epoch from disk
        # + back up best epoch weights in memory
        # + restore the kmodel to latest epoch from memory state so that
        #   training can resume
        else:
            # --------------------------------------------------------03.01
            # --------------------------------------------------------03.02
            # If we are here then there are chkpt_manager on the disk. Note
            # that the fit lifecycle will restore kmodel to latest epoch. We
            # need to confirm that restored kmodel is at correct epoch i.e.
            # `_latest_epoch`, also we want to backup the weights in memory.
            # Both of these things are achieved by creating `InMemoryChkpt`
            # object.
            # noinspection PyAttributeOutsideInit
            self.latest = self.InMemoryChkpt(
                epoch=_latest_epoch,
                smart_chkpt=self.manager.model.chkpt,
            )
            # --------------------------------------------------------03.03
            # restore best_epoch from disk so that we can backup checkpoint in
            # memory
            if _best_epoch != _latest_epoch:
                self.manager.model.restore_to_best_epoch()
            # --------------------------------------------------------03.04
            # back up best epoch weights in memory
            # noinspection PyAttributeOutsideInit
            self.best = self.InMemoryChkpt(
                epoch=_best_epoch,
                smart_chkpt=self.manager.model.chkpt,
            )
            # --------------------------------------------------------03.05
            # now we restore latest from memory ... also note that this is
            # retained in kmodel ... so that fit can resume based on state of
            # latest checkpoint rather than that of the best
            self.latest.restore()
        
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs = None
    ):
        # ------------------------------------------------------------01
        # get latest and best epoch
        _latest_epoch = self.manager.model.latest_epoch
        _best_epoch = self.manager.model.best_epoch

        # ------------------------------------------------------------02
        # we assume here that History callback have saved results to disk
        # but we still do a redundant check here
        # todo: remove redundant check here
        e.code.AssertError(
            value1=_latest_epoch, value2=epoch,
            msgs=[
                f"We expect the latest epoch to be same epoch as passed here",
                f"this can happen if ModelCheckpoint callback is called before "
                f"History callback"
            ]
        )

        # ------------------------------------------------------------03
        # move internal epoch variable to incoming epoch ... as we have
        # trained until that epoch ... plus we will be backing those weights
        # in in_memory_chkpt
        self.manager.model.chkpt.variables['epoch'].assign(epoch)

        # ------------------------------------------------------------04
        # `latest` needs to be always set ...
        # note that this will also check if the kmodel is trained until
        # _latest_epoch
        # noinspection PyAttributeOutsideInit
        self.latest = self.InMemoryChkpt(
            epoch=_latest_epoch,
            smart_chkpt=self.manager.model.chkpt,
        )
        
        # ------------------------------------------------------------05
        # decide if we need to set `best`
        if self.best is None:
            _set_best = True
        else:
            # check if best epoch is changed
            if self.best.epoch != _best_epoch:
                # if changed then best epoch will be same as latest epoch
                e.code.AssertError(
                    value1=_best_epoch,
                    value2=_latest_epoch,
                    msgs=[
                        f"Best epoch and latest epoch will be same if we need "
                        f"to update weights for best epoch"
                    ]
                )
                _set_best = True
            else:
                _set_best = False
        
        # ------------------------------------------------------------06
        # set `best` if needed
        if _set_best:
            # note that here _best_epoch == _latest_epoch
            # this is because as we are changing best epoch that means latest
            # epoch is doing better ... but anyways we duplicate the weights
            # noinspection PyAttributeOutsideInit
            self.best = self.InMemoryChkpt(
                epoch=_best_epoch,
                smart_chkpt=self.manager.model.chkpt,
            )
            
    def on_fit_exit(self):
        # ------------------------------------------------------------01
        # if there is no latest and best epoch that means epoch was never
        # called or was interrupted in between ... in that case return
        if self.latest is None:
            if self.best is not None:
                e.code.ShouldNeverHappen(msgs=[])
            return
            
        # ------------------------------------------------------------02
        # get latest and best epoch
        _latest_epoch = self.manager.model.latest_epoch
        _best_epoch = self.manager.model.best_epoch
        
        # ------------------------------------------------------------03
        # the latest and best epoch based on history on disk should match in
        # memory model weights
        e.code.AssertError(
            value1=_latest_epoch, value2=self.latest.epoch,
            msgs=[
                f"The latest epoch from history on disk and latest epoch in "
                f"memory does not match."
            ]
        )
        e.code.AssertError(
            value1=_best_epoch, value2=self.best.epoch,
            msgs=[
                f"The best epoch from history on disk and best epoch in "
                f"memory does not match."
            ]
        )
        
        # ------------------------------------------------------------04
        # time to save on disk ... first save the best then the latest ... This
        # is needed because if the best is less than the latest then that will
        # trigger error that the epoch to save is not the greatest
        # if `best` epoch not on disk then only save
        if _best_epoch not in self.manager.model.epochs_on_disk:
            # restore from in memory models
            self.best.restore()
            # save it to disk
            self.manager.model.save()
        # `latest` epoch will never be on disk
        if _latest_epoch in self.manager.model.epochs_on_disk:
            # if latest and best epoch are same the above code will end up
            # saving also the latest epoch ... if they are not same then this
            # is problem
            if _best_epoch != _best_epoch:
                e.code.ShouldNeverHappen(
                    msgs=[f"The latest epoch {_latest_epoch} is already on the "
                          f"disk"])
        else:
            # restore from in memory models
            self.latest.restore()
            # save it to disk
            self.manager.model.save()
        
        # ------------------------------------------------------------05
        # remove unnecessary chkpt_manager on disk
        self.manager.model.delete_useless_checkpoints()
        
        
@dataclasses.dataclass
class Logger(Callback):
    """
    
    We will eventually override this logger to use our logging system.
    Most likely we do not want to extend ProgbarLogger and instead use spinner.

    todo: undo validation check in CallbackListEnhanced.__init__ to see that
      `ProgbarLogger` is no longer allowed.
      
    >>> tk.callbacks.ProgbarLogger
    """
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs
    ):
        _results = logs.validate_results
        _dict = {
            'epoch': f"{epoch:04d}",
            'acc': f"{_results['sparse_categorical_accuracy']:2.5f}",
            'loss': f"{_results['loss']:2.5f}"
        }
        print(_dict)
