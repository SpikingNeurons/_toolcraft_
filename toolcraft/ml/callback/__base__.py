"""
If you override periodic_task() method of Callback it becomes a Callback that
can be periodically called with a parallel process from CallbacksManager.

While ParallelCallback gets one thread per callback to run in parallel and is
communicated with SIGNAL messaging ... optionally it can also be used by
periodic_task

Note that there is only one process for periodic_task per CallbacksManager.
"""

import typing as t
import dataclasses
import time
import random
import multiprocessing as mp

from ... import logger
from ... import error as e
from ... import util
from . import logs as lm

# noinspection PyUnreachableCode
if False:
    from .. import Model

_LOGGER = logger.get_logger()

# noinspection PyUnresolvedReferences,PyUnreachableCode
if False:
    from .. import ml as mm


# noinspection PyMethodMayBeStatic
@dataclasses.dataclass
class Callback:
    """
    The Life cycle of callback
    + The periodic_task will modify state of callback periodically
    + For fit: i.e. train and evaluate
      - on_fit_enter
        - on_epoch_start
          - on_train_start
            - on_train_batch_start
            - on_train_batch_end
          - on_train_end
          - on_validate_start
            - on_validate_batch_start
            - on_validate_batch_end
          - on_validate_end
        - on_epoch_end
      - on_fit_exit
    + For prediction
      - on_predict_start
        - on_predict_batch_start
        - on_predict_batch_end
      - on_predict_end
      
    todo: add pickle support for callback ... we will provide some concrete
      variable store and restore based on FileGroup oy py_arrow ...
      instead of using pickle
      
    When using periodic task when executing you want the periodic_task before
    exit ... then you need to use *_end method (expect for batch)
    """
    
    manager: "CallbacksManager" = dataclasses.field(init=False)
    
    # noinspection PyTypeChecker
    @property
    def periodic_task_after_secs(self) -> int:
        return None
    
    def __post_init__(self):
        
        # init
        self.init_validate()
        self.init()
    
    @staticmethod
    def _raise_err():
        e.code.CodingError(
            msgs=[
                f"Ideally should never be called as we have implemented "
                f"efficient properties in callback manager starting with cbs_* "
                f"which efficiently call only this callback when "
                f"respective method is overridden",
                f"Also, make sure to not call super() in overridden method"
            ]
        )
        
    def init(self):
        ...
    
    def init_validate(self):
        
        # ---------------------------------------------------------------- 01
        # if the callback class has overridden periodic_task
        # then the callback is eligible to be used by periodic_task process
        if Callback.periodic_task != self.__class__.periodic_task:
            # since it is eligible the callback should override property
            # periodic_task_after_secs
            if self.periodic_task_after_secs is None:
                e.code.CodingError(
                    msgs=[
                        f"Please override property "
                        f"`{Callback.periodic_task_after_secs.fget.__name__}` "
                        f"as you have overridden method "
                        f"`{self.periodic_task.__name__}` "
                        f"in class {self.__class__}"
                    ]
                )
        else:
            if self.periodic_task_after_secs is not None:
                e.code.CodingError(
                    msgs=[
                        f"Please do not override property "
                        f"`periodic_task_after_secs` as you have not "
                        f"overridden method {self.periodic_task} in class "
                        f"{self.__class__}"
                    ]
                )
                
    def set_manager(self, manager: "CallbacksManager"):
        self.manager = manager
    
    def periodic_task(self):
        """
        Have some flags here that are set periodically in this method.
        Reading those flags the Callback methods will perform actions.
        
        That is how periodic tasks work.
        """
        self._raise_err()
        
    def on_fit_enter(self):
        """
        Called when you enter fit ... within which multiple epochs are called
        for training and evaluation.
        
        Useful for resuming training sessions.
        """
        self._raise_err()
    
    def on_epoch_start(
        self, epoch: int, logs: lm.EpochStartLogs
    ):
        """Called at the start of an epoch.
    
        Subclasses should override for any actions to run. This function
        should only be called during TRAIN mode.
    
        Arguments:
            epoch: integer, index of epoch.
            logs: EpochStartLogs (currently pass None as no fields)
        """
        self._raise_err()
    
    def on_train_start(self, logs: lm.PhaseStartLogs):
        """
        Called at the beginning of `fit`.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            logs: PhaseStartLogs (currently pass None as no fields)
        """
        self._raise_err()
    
    def on_train_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        """
        Called at the beginning of a training batch in `fit` methods.

        Subclasses should override for any actions to run.
    
        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: BatchStartLogs
        """
        self._raise_err()
    
    def on_train_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        """
        Called at the end of a training batch in `fit` methods.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: BatchEndLogs
        """
        self._raise_err()
    
    def on_train_end(self, logs: lm.PhaseEndLogs):
        """
        Called at the end of `fit`.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            logs: PhaseEndLogs (currently pass None as no fields)
        """
        self._raise_err()
    
    def on_validate_start(self, logs: lm.PhaseStartLogs):
        """
        Called at the beginning of `evaluate`.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            logs: PhaseStartLogs (currently pass None as no fields)
        """
        self._raise_err()
    
    def on_validate_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        """
        Called at the beginning of a training batch in `evaluate` methods.

        Subclasses should override for any actions to run.
    
        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: BatchStartLogs
        """
        self._raise_err()
    
    def on_validate_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        """
        Called at the end of a training batch in `evaluate` methods.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: BatchEndLogs
        """
        self._raise_err()
    
    def on_validate_end(self, logs: lm.PhaseEndLogs):
        """
        Called at the end of `evaluate`.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            logs: PhaseEndLogs (currently pass None as no fields)
        """
        self._raise_err()
    
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs
    ):
        """Called at the end of an epoch.
    
        Subclasses should override for any actions to run. This function
        should only be called during TRAIN mode.
    
        Arguments:
            epoch: integer, index of epoch.
            logs: EpochEndLogs
        """
        self._raise_err()
        
    def on_fit_exit(self):
        """
        Called when you exit fit ... after multiple epochs are called
        for training and evaluation.
        
        Useful for resuming training sessions.
        """
        self._raise_err()
    
    def on_predict_start(self, logs: lm.PhaseStartLogs):
        """
        Called at the beginning of `predict`.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            logs: PhaseStartLogs (currently pass None as no fields)
        """
        self._raise_err()
    
    def on_predict_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        """
        Called at the beginning of a training batch in `predict` methods.

        Subclasses should override for any actions to run.
    
        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: BatchStartLogs
        """
        self._raise_err()
    
    def on_predict_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        """
        Called at the end of a training batch in `predict` methods.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            batch: integer, index of batch within the current epoch.
            logs: BatchEndLogs
        """
        self._raise_err()
    
    def on_predict_end(self, logs: lm.PhaseEndLogs):
        """
        Called at the end of `predict`.
    
        Subclasses should override for any actions to run.
    
        Arguments:
            logs: PhaseEndLogs (currently pass None as no fields)
        """
        self._raise_err()


@dataclasses.dataclass
class ParallelCallback(util.Process, Callback):
    """
    todo: still not tested ... check examples/try_callback.py
    A callback that executes as a parallel process and still can be managed
    by CallbacksManager

    Used to make any callback to spawn a parallel process that can be
    signaled to do things in parallel

    Note the periodic task process in CallbackManager has different purpose
    of calling periodic_task and can be used by any callback that overrides the
    self.periodic_task .... periodic task process is only one and central to
    CallbackManager ....

    The periodic process in CallbacksManager can still call
    overriden self.periodic_task periodically if you override it ....
      - ~~ See example callback.fitter.Validator ~~ (refer folder _callback)
      - todo we no longer want to have Validation as parallel callback as
          validation does not fit in callback design and should be part of
          fit logic like keras .... but nonetheless we will explore code to
          use parallel callbacks somewhere else like ... uploading files to
          cloud in parallel .... logging in async to remote server
      
    Note that this class is also a regular callback so you can use callback
    methods to signal process via self.do_it() method and pass the signal.
    But make sure that self.start() and self.close() is appropriately called
    to spawn the process.
    You can also call start and close in one of the callback methods based on
    use case. That is for example when training epoch starts you can start in
    on_epoch_start and close thread in on_epoch_end.
    
    Note that on_* methods in this class are responsible to signal parallel
    process of ParallelCallback. While the actual logic need to be
    implemented in p_on_* methods.
    
    todo: figure out how to communicate method arguments like epoch, batch,
      logs to parallel process ... or may be never use parallel process to
      depend on batch or phase or epoch results
    """
    class SIGNAL(util.Process.SIGNAL):
        periodic_task = "periodic_task"
        on_fit_enter = "on_fit_enter"
        on_epoch_start = "on_epoch_start"
        on_fit_start = "on_train_start"
        on_fit_batch_start = "on_train_batch_start"
        on_fit_batch_end = "on_train_batch_end"
        on_fit_end = "on_train_end"
        on_validate_start = "on_validate_start"
        on_validate_batch_start = "on_validate_batch_start"
        on_validate_batch_end = "on_validate_batch_end"
        on_validate_end = "on_validate_end"
        on_epoch_end = "on_epoch_end"
        on_fit_exit = "on_fit_exit"
        on_predict_start = "on_predict_start"
        on_predict_batch_start = "on_predict_batch_start"
        on_predict_batch_end = "on_predict_batch_end"
        on_predict_end = "on_predict_end"
        
    name: str = dataclasses.field(init=False)
    
    # the process is alive until the lifetime of instance
    auto_start_and_close: bool = dataclasses.field(init=False)
    
    def __post_init__(self):
        # call callback __post_init__
        Callback.__post_init__(self)
        
        # init fields of util.Process as it has no init_fields method
        self.name = f"{self.__class__.__name__}.ParallelCallback"
        self.auto_start_and_close = True
        
        # call util.Process __post_init__
        util.Process.__post_init__(self)
    
    def periodic_task(self):
        self.process_send_signal(signal=self.SIGNAL.periodic_task)
        
    def on_fit_enter(self):
        self.process_send_signal(signal=self.SIGNAL.on_fit_enter)

    def on_epoch_start(
            self, epoch: int, logs: lm.EpochStartLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_epoch_start)
    
    def on_train_start(self, logs: lm.PhaseStartLogs):
        self.process_send_signal(signal=self.SIGNAL.on_fit_start)
    
    def on_train_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_fit_batch_start)
    
    def on_train_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_fit_batch_end)
    
    def on_train_end(self, logs: lm.PhaseEndLogs):
        self.process_send_signal(signal=self.SIGNAL.on_fit_end)
    
    def on_validate_start(self, logs: lm.PhaseStartLogs):
        self.process_send_signal(signal=self.SIGNAL.on_validate_start)
    
    def on_validate_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_validate_batch_start)
    
    def on_validate_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_validate_batch_end)
    
    def on_validate_end(self, logs: lm.PhaseEndLogs):
        self.process_send_signal(signal=self.SIGNAL.on_validate_end)
    
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_epoch_end)
        
    def on_fit_exit(self):
        self.process_send_signal(signal=self.SIGNAL.on_fit_exit)
    
    def on_predict_start(self, logs: lm.PhaseStartLogs):
        self.process_send_signal(signal=self.SIGNAL.on_predict_start)
    
    def on_predict_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_predict_batch_start)
    
    def on_predict_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        self.process_send_signal(signal=self.SIGNAL.on_predict_batch_end)
    
    def on_predict_end(self, logs: lm.PhaseEndLogs):
        self.process_send_signal(signal=self.SIGNAL.on_predict_end)
    
    def process_fn(self, signal: str):
        # note that signal will already be checked in util.Process
        _method_name = f"p_{signal}"
        _method = getattr(self, _method_name)
        _method()

    def p_periodic_task(self):
        self._raise_err()

    def p_on_fit_enter(self):
        self._raise_err()

    def p_on_epoch_start(self):
        self._raise_err()

    def p_on_fit_start(self):
        self._raise_err()

    def p_on_fit_batch_start(self):
        self._raise_err()

    def p_on_fit_batch_end(self):
        self._raise_err()

    def p_on_fit_end(self):
        self._raise_err()

    def p_on_validate_start(self):
        self._raise_err()

    def p_on_validate_batch_start(self):
        self._raise_err()

    def p_on_validate_batch_end(self):
        self._raise_err()

    def p_on_validate_end(self):
        self._raise_err()

    def p_on_epoch_end(self):
        self._raise_err()

    def p_on_fit_exit(self):
        self._raise_err()

    def p_on_predict_start(self):
        self._raise_err()

    def p_on_predict_batch_start(self):
        self._raise_err()

    def p_on_predict_batch_end(self):
        self._raise_err()

    def p_on_predict_end(self):
        self._raise_err()


@dataclasses.dataclass
class PeriodicTaskScheduler(util.Process):
    """
    PeriodicTaskScheduler is a parallel process per CallbacksManager instance
    which informs all callbacks to take actions periodically.
    """
    
    class SIGNAL(util.Process.SIGNAL):
        run_loop = "run_loop"
        
    num_of_periodic_tasks: int
    tasks_periodicity: mp.Array
    
    # task schedule
    tasks_schedule: mp.Array = dataclasses.field(init=False)
    # we cannot add any custom signal here as we have infinite loop in 
    # process_fn so the util.Process will never receive signal as the code 
    # will be waiting in the loop .... so instead we rely on variable stop
    stop: mp.Value = dataclasses.field(init=False)
    
    def __post_init__(self):
        
        # --------------------------------------------------------------- 01
        # assign stop value that will be used to break while loop in
        # overriden process_fn
        self.stop = mp.Value('i', 0)
        
        # --------------------------------------------------------------- 02
        # the periodic_task_process will update this array so that main
        # thread knows what to execute
        # todo ... need to check how efficient this approach is ??/
        #   https://docs.python.org/3.8/library/multiprocessing.html#
        #   sharing-state-between-processes
        self.tasks_schedule = mp.Array('i', [
            0 for _ in range(self.num_of_periodic_tasks)
        ])
        
        # --------------------------------------------------------------- 03
        # call super
        super().__post_init__()

    def process_run_loop(self):
        # --------------------------------------------------------------- 01
        # signal to run the loop
        self.process_send_signal(signal=self.SIGNAL.run_loop)
    
    def process_fn(self, signal: str):
        _tick = 1
        while True:
            
            # if killer val break
            if self.stop.value == 1:
                break
            
            # sleep for one tick
            time.sleep(1)
            
            # loop over after sec array to update tracker array so that
            # main thread can process periodic_task
            for cb_id, after_sec in enumerate(self.tasks_periodicity):
                if _tick % after_sec == 0:
                    # todo: can enhance to keep count of how many times it
                    #  was done
                    self.tasks_schedule[cb_id] = 1
                    
            # increment tick
            _tick += 1
            
            # safety reset to avoid overflow
            # 32 bit limit is 2147483647 ... we make it 214748364
            if _tick > 214748364:
                # reset to something random ;)
                _tick = random.randint(100000, 1000000)
                
    def process_start(self):
        # this is to let the while loop in process_fn
        self.stop.value = 0
        # this is to tell the infinite loop of process to start
        super().process_start()
        
    def process_close(self):
        # this is to let the while loop in process_fn
        self.stop.value = 1
        # this is to tell the infinite loop of process to break
        super().process_close()


@dataclasses.dataclass
class CallbacksManager:
    callbacks: t.List[Callback]
    model: "Model"
            
    @property
    @util.CacheResult
    def cbs_periodic_task(self) -> t.Dict[int, Callback]:
        _cbs = self._filter_callbacks_if_not_default(
            method_name="periodic_task"
        )
        # returning a dict so that dict key serves as callback id ... just
        # for efficient communication
        return {
            i: v for i, v in enumerate(_cbs)
        }
    
    @property
    @util.CacheResult
    def cbs_on_fit_enter(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_fit_enter")
    
    @property
    @util.CacheResult
    def cbs_on_epoch_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_epoch_start")
    
    @property
    @util.CacheResult
    def cbs_on_train_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_train_start")
    
    @property
    @util.CacheResult
    def cbs_on_train_batch_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_train_batch_start")
    
    @property
    @util.CacheResult
    def cbs_on_train_batch_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_train_batch_end")
    
    @property
    @util.CacheResult
    def cbs_on_train_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_train_end")
    
    @property
    @util.CacheResult
    def cbs_on_validate_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_validate_start")
    
    @property
    @util.CacheResult
    def cbs_on_validate_batch_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_validate_batch_start")
    
    @property
    @util.CacheResult
    def cbs_on_validate_batch_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_validate_batch_end")
    
    @property
    @util.CacheResult
    def cbs_on_validate_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_validate_end")
    
    @property
    @util.CacheResult
    def cbs_on_epoch_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_epoch_end")
    
    @property
    @util.CacheResult
    def cbs_on_fit_exit(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_fit_exit")
    
    @property
    @util.CacheResult
    def cbs_on_predict_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_predict_start")
    
    @property
    @util.CacheResult
    def cbs_on_predict_batch_start(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_predict_batch_start")
    
    @property
    @util.CacheResult
    def cbs_on_predict_batch_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_predict_batch_end")
    
    @property
    @util.CacheResult
    def cbs_on_predict_end(self) -> t.List[Callback]:
        return self._filter_callbacks_if_not_default(
            method_name="on_predict_end")
    
    @property
    @util.CacheResult
    def periodic_task_scheduler(self) -> PeriodicTaskScheduler:
        """
        
        Returns:
            PeriodicTaskScheduler when there are callbacks that have periodic
            task else None
        """
        
        # the periodicity of each task in seconds
        _num_of_periodic_tasks = len(self.cbs_periodic_task)
        _tasks_periodicity = mp.Array(
            'i', [
                self.cbs_periodic_task[i].periodic_task_after_secs
                for i in range(_num_of_periodic_tasks)
            ]
        )
        return PeriodicTaskScheduler(
            name=f"{self.__class__.__name__}.PeriodicTask",
            num_of_periodic_tasks=_num_of_periodic_tasks,
            tasks_periodicity=_tasks_periodicity,
        )
    
    def __post_init__(self):

        # --------------------------------------------------------------- 01
        # add default callbacks
        self._add_default_callbacks()

        # --------------------------------------------------------------- 02
        # perform validation
        self.init_validate()

        # --------------------------------------------------------------- 03
        # set manager in all callbacks
        for cb in self.callbacks:
            cb.set_manager(self)
    
    def __enter__(self) -> "CallbacksManager":

        # --------------------------------------------------------------- 01
        # call property periodic_task_scheduler so that the periodic task
        # process thread starts of needed
        pts = self.periodic_task_scheduler
        if pts is not None:
            # we will need to start the parallel process
            pts.process_start()
            # we need to run the infinite time loop that will call periodic
            # task of all relevant callbacks
            pts.process_run_loop()
            
        # --------------------------------------------------------------- 02
        # return self
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # --------------------------------------------------------------- 01
        # if there is any callback that uses periodic task then we will not
        # get None ... then in that case close the parallel process related
        # periodic_task
        pts = self.periodic_task_scheduler
        if pts is not None:
            pts.process_close()
    
    def _filter_callbacks_if_not_default(self, method_name: str):
        _ret = []
        for cb in self.callbacks:
            # ---------------------------
            # get method name and class
            # defaults
            _method_name = method_name
            _class = Callback
            # if parallel callback change defaults
            if isinstance(cb, ParallelCallback):
                if method_name != "periodic_task":
                    _method_name = f"p_{method_name}"
                _class = ParallelCallback
            
            # ---------------------------
            # check if overridden and append
            if getattr(cb.__class__, _method_name) != \
                    getattr(_class, _method_name):
                _ret.append(cb)
                
        return _ret
    
    def _add_default_callbacks(self):
        from . import cbs
        self.callbacks.extend(
            [
                cbs.History(),
                cbs.ModelCheckpoint(),
                cbs.Logger(),
                cbs.StopTrainingSemaphore(),
            ]
        )
    
    def init_validate(self):
        
        # --------------------------------------------------------------- 01
        # check if some callbacks are repeated
        cb_classes = [cb.__class__ for cb in self.callbacks]
        for cbc in cb_classes:
            cbc_like = [_cbc for _cbc in cb_classes if _cbc is cbc]
            if len(cbc_like) != 1:
                e.validation.NotAllowed(
                    msgs=[
                        f"Multiple instances i.e. {len(cbc_like)} for callback "
                        f"class {cbc} were found in callbacks manager list",
                        f"There should be only one instance present.",
                        f"Make sure that you do not supply callbacks added in "
                        f"`_add_default_callbacks` as we will take care of it."
                    ]
                )
        
        # --------------------------------------------------------------- 02
        # some things are mandatory
        # Also, check if history callback is before ModelCheckpoint
        # todo: this is very strict ... we might need to change this in future
        from . import cbs
        _history_cb_present = False
        _model_checkpoint_cb_present = False
        for cb in self.callbacks:
            if isinstance(cb, cbs.History):
                _history_cb_present = True
            if isinstance(cb, cbs.ModelCheckpoint):
                if _history_cb_present:
                    _model_checkpoint_cb_present = True
                    break
                else:
                    e.validation.NotAllowed(
                        msgs=[
                            f"Please make sure that {cbs.History} callback is "
                            f"supplied before {cbs.ModelCheckpoint} callback."
                        ]
                    )
        _extra_msgs = []
        if not _history_cb_present:
            _extra_msgs.append(
                f"Please supply {cbs.History} callback."
            )
        if not _model_checkpoint_cb_present:
            _extra_msgs.append(
                f"Please supply {cbs.ModelCheckpoint} callback."
            )
        if bool(_extra_msgs):
            e.validation.NotAllowed(msgs=_extra_msgs)
        
    def periodic_task(self):
        # loop over all cbs for periodic task
        for cb_id, flag in enumerate(
            self.periodic_task_scheduler.tasks_schedule
        ):
            # check if the periodic task process requested the task to be
            # executed
            if flag == 1:
                # get callback based on callback id
                cb = self.cbs_periodic_task[cb_id]
                # execute task
                cb.periodic_task()
                # reset the tracker
                self.periodic_task_scheduler.tasks_schedule[cb_id] = 0
                
    def on_fit_enter(self):
        # todo: might not need the periodic_task_scheduler
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_fit_enter:
            cb.on_fit_enter()
                
    def on_epoch_start(
        self, epoch: int, logs: lm.EpochStartLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_epoch_start:
            cb.on_epoch_start(epoch=epoch, logs=logs)
                
    def on_train_start(self, logs: lm.PhaseStartLogs):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_train_start:
            cb.on_train_start(logs=logs)
                
    def on_train_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_train_batch_start:
            cb.on_train_batch_start(batch=batch, logs=logs)
                
    def on_train_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_train_batch_end:
            cb.on_train_batch_end(batch=batch, logs=logs)
                
    def on_train_end(self, logs: lm.PhaseEndLogs):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_train_end:
            cb.on_train_end(logs=logs)
                
    def on_validate_start(self, logs: lm.PhaseStartLogs):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_validate_start:
            cb.on_validate_start(logs=logs)
                
    def on_validate_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_validate_batch_start:
            cb.on_validate_batch_start(batch=batch, logs=logs)
                
    def on_validate_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        for cb in self.cbs_on_validate_batch_end:
            cb.on_validate_batch_end(batch=batch, logs=logs)
                
    def on_validate_end(self, logs: lm.PhaseEndLogs):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_validate_end:
            cb.on_validate_end(logs=logs)
                
    def on_epoch_end(
        self, epoch: int, logs: lm.EpochEndLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_epoch_end:
            cb.on_epoch_end(epoch=epoch, logs=logs)
            
    def on_fit_exit(self):
        # todo: might not need the periodic_task_scheduler
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_fit_exit:
            cb.on_fit_exit()
                
    def on_predict_start(self, logs: lm.PhaseStartLogs):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_predict_start:
            cb.on_predict_start(logs=logs)
                
    def on_predict_batch_start(
        self, batch: int, logs: lm.BatchStartLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_predict_batch_start:
            cb.on_predict_batch_start(batch=batch, logs=logs)
                
    def on_predict_batch_end(
        self, batch: int, logs: lm.BatchEndLogs
    ):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_predict_batch_end:
            cb.on_predict_batch_end(batch=batch, logs=logs)
                
    def on_predict_end(self, logs: lm.PhaseEndLogs):
        if self.periodic_task_scheduler is not None:
            self.periodic_task()
        for cb in self.cbs_on_predict_end:
            cb.on_predict_end(logs=logs)
