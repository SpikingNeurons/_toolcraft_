"""
Module that will hold code to do state management
"""

import dataclasses
import pathlib
import typing as t
import datetime
import abc

from .. import error as e
from .. import util, settings
from .. import marshalling as m


class Suffix:
    info = ".info"
    config = ".config"


@dataclasses.dataclass
class StateFile(m.Tracker, abc.ABC):
    hashable: m.HashableClass
    root_dir_str: str

    @property
    @util.CacheResult
    def path(self) -> pathlib.Path:
        return pathlib.Path(self.root_dir_str) / \
            f"{self.hashable.name}{self.suffix}"

    @property
    @abc.abstractmethod
    def suffix(self) -> str:
        ...

    @abc.abstractmethod
    def sync(self):
        ...

    @abc.abstractmethod
    def delete(self):
        ...


@dataclasses.dataclass
class Info(StateFile):

    @property
    @util.CacheResult
    def backup_path(self) -> pathlib.Path:
        e.code.AssertError(
            value1=settings.FileHash.DEBUG_HASHABLE_STATE, value2=True,
            msgs=[
                f"This property can be used only when you have configured "
                f"`config.DEBUG_HASHABLE_STATE=True`"
            ]
        )
        return self.path.parent / f"_backup_{self.path.name}_backup_"

    @property
    def suffix(self) -> str:
        return Suffix.info

    def sync(self):
        """
        The info on disk if available must match.
        Also note that we only sync hashable. Note that if hashable is
        StorageHashable we might have parent_folder info inside it but this
        class wants to support all HashableClass. So we need extra argument
        parent_folder
        """
        _yaml = self.hashable.yaml()
        if self.path.exists():
            _yaml_on_disk = self.path.read_text()
            if _yaml_on_disk != _yaml:
                e.code.CodingError(
                    msgs=[
                        "Info file mismatch ... should never happen",
                        "State on disk: ",
                        [_yaml_on_disk],
                        "State in memory: ",
                        [_yaml],
                    ]
                )
        else:
            # handle info file and make it read only
            # ... write hashable info
            self.path.write_text(_yaml)
            # ... make read only as done only once
            util.io_make_path_read_only(self.path)

    def delete(self):
        util.io_make_path_editable(self.path)
        self.path.unlink()


class ConfigInternal(m.Internal):

    start_syncing: bool = False

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + ['start_syncing']


@dataclasses.dataclass
class Config(StateFile):
    """
    todo: update to replace LOCK_ACCESS_FLAG mechanism with internal property
      + move even all below thing sto internal property
        LOCK_ACCESS_FLAG
        BACKUP_YAML_STR_KEY
    """

    # note that created on refers to hashable class of which config is a
    # property ... but we cannot have that field in there as it will affect
    # its unique hex_hash value
    # time when info file was created
    created_on: datetime.datetime = None
    # time when config file was updated ... i.e. when access happened etc
    config_updated_on: t.List[datetime.datetime] = dataclasses.field(
        default_factory=list
    )

    class LITERAL(StateFile.LITERAL):
        config_updated_on_list_limit = 10

    @property
    @util.CacheResult
    def internal(self) -> ConfigInternal:
        return ConfigInternal(owner=self)

    @property
    def suffix(self) -> str:
        return Suffix.config

    @property
    @util.CacheResult
    def dataclass_field_names(self) -> t.List[str]:
        return [
            f_name for f_name in super().dataclass_field_names
            if f_name not in ["hashable", "root_dir_str"]
        ]

    def __post_init__(self):
        """
        __post_init__ is allowed as it is not m.HashableClass
        """

        # ------------------------------------------------------------ 01
        # if path exists load data dict from it
        # that is sync with contents on disk
        if self.path.exists():
            _hashable_dict_from_disk = \
                m.FrozenDict.from_yaml(self.path.read_text())
            # update internal dict from HashableDict loaded from disk
            self.__dict__.update(
                _hashable_dict_from_disk.get()
            )

        # ------------------------------------------------------------ 02
        # start syncing i.e. any updates via __setattr__ will be synced
        # to disc
        self.internal.start_syncing = True

    def __setattr__(self, key, value):

        # for key in dataclass field names then if any of it is list or dict
        # make them special notifier based proxy list and dict
        if key in self.dataclass_field_names:
            if value.__class__ == list:
                # noinspection PyPep8Naming
                NotifierList = \
                    util.notifying_list_dict_class_factory(list, self.sync)
                value = NotifierList(value)
            elif value.__class__ == dict:
                # noinspection PyPep8Naming
                NotifierDict = \
                    util.notifying_list_dict_class_factory(dict, self.sync)
                value = NotifierDict(value)
            else:
                ...

        # call super to set things
        super().__setattr__(key, value)

        # We call sync always as this will occur less frequently compared to
        # __getattribute__
        # Note that list and dict updates will be automatically handled by
        # notifier version
        if self.internal.start_syncing:
            self.sync()

    def __call__(self) -> "Config":
        # todo: remove this
        raise Exception("NO LONGER SUPPORTED")

    def make_yaml_str_from_current_state(self) -> str:
        # here we convert proxy notifier list and dict back to normal python
        # builtins
        _dict = {}
        for f_name in self.dataclass_field_names:
            value = getattr(self, f_name)
            if isinstance(value, list):
                value = list(value)
            if isinstance(value, dict):
                value = dict(value)
            _dict[f_name] = value

        # noinspection PyTypeChecker
        return m.FrozenDict(item=_dict).yaml()

    def sync(self):
        # -------------------------------------------------- 01
        # get current state
        _current_state = self.make_yaml_str_from_current_state()

        # -------------------------------------------------- 02
        # if file exists on the disk then check if the contents are different
        # this helps us catch unexpected syncs
        # if the contents are same then we raise error as nothing is there to
        # update
        if self.path.exists():
            _disk_state = self.path.read_text()
            if _current_state == _disk_state:
                e.code.CodingError(
                    msgs=[
                        f"We expect the state on disk to be different to "
                        f"internal state for config ...",
                        {
                            "_current_state": _current_state,
                            "_disk_state": _disk_state
                        },
                        f"This looks like unexpected sync as nothing has "
                        f"changed in config"
                    ]
                )

        # -------------------------------------------------- 04
        # write to disk
        self.path.write_text(_current_state)

    def delete(self):
        # delete associated file on the disk
        self.path.unlink()

        # also reset the config based on default values
        # this we achieve by creating new object on the fly ...
        # Note we can also wipe cache using
        # `util.WipeCacheResult("config", self.hashable)` but that will not
        # help as this object itself is cached
        # noinspection PyArgumentList
        # The below code will trigger __post_init__ so list and dict will be
        # converted to Notifier proxies anyways
        _default_config = self.__class__(
            hashable=self.hashable, root_dir_str=self.root_dir_str
        )

        # Note that this will not trigger __setattr__
        self.__dict__.update(
            _default_config.__dict__
        )


@dataclasses.dataclass
class StateManager(m.Tracker):
    """
    Manages the state of HashableClass
    + save class info in *.info file that has hex value
    + save config info in *.config file ... note that config does not affect
      the *.info file

    todo: We can have the state manager via some decorator like
      storage.StoreField where we create two data frames one for info and other
      for config. Then we can stream them or store to some database where we
      can retrieve them ....
      As of now we limit them to be saved alongside FileGroup, DfFile and
      Folder ... and hence this class does not make sense here but instead
      should be moved to storage module ....
      But we might have more usage for this so we will retain here
    """
    hashable: m.HashableClass
    root_dir_str: str
    config: Config

    @property
    @util.CacheResult
    def info(self) -> Info:
        return Info(hashable=self.hashable, root_dir_str=self.root_dir_str)

    @property
    def is_available(self) -> bool:
        # check if file present
        _info_file_there = self.info.path.is_file()
        _config_file_there = self.config.path.is_file()

        # if one is present and other is not raise error
        if _info_file_there ^ _config_file_there:
            e.code.CodingError(
                msgs=[
                    f"We expect either both files to be present or none to be "
                    f"present",
                    f"It seems you have only one of the files",
                    {
                        "_info_file_there": _info_file_there,
                        "_config_file_there": _config_file_there
                    },
                    f"In case this error occur during execution of "
                    f"create_post_runner then may be you have updated config "
                    f"before calling sync. Try to do updates to config after "
                    f"making call to super where created_on time stamp is "
                    f"added using sync() method ..."
                ]
            )

        # return
        return _info_file_there

    @property
    def is_backup_available(self) -> bool:
        return self.info.backup_path.is_file()

    def delete(self):
        # delete state files if on disk
        if self.is_available:
            self.info.delete()
            self.config.delete()
        else:
            e.code.CodingError(
                msgs=[
                    f"We do not have the state for hashable so we cannot "
                    f"delete it",
                    f"Did you forget to call {self.__class__.sync_to_disk} "
                    f"or else you need to check if state is available on "
                    f"disk first using property `self.is_available`"
                ]
            )

    def sync_to_disk(self):
        # ----------------------------------------------------------- 01
        # just call sync
        # + if present will check the file on disk with internal state
        # + else will create file
        self.info.sync()
        # ----------------------------------------------------------- 02
        # just update created_on it will auto sync
        self.config.created_on = datetime.datetime.now()
