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


@dataclasses.dataclass
class Config(StateFile):

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

        # helper vars for instance Config StateFile
        # we add this attribute to self to lock access in get and set methods
        LOCK_ACCESS_FLAG = "__lock_access__"
        HASHABLE_FIELDS_LIST_KEY = "__hashable_fields__"
        BACKUP_YAML_STR_KEY = "__backup_yaml_str__"

    @property
    def suffix(self) -> str:
        return Suffix.config

    def __post_init__(self):
        """
        __post_init__ is allowed as it is not m.HashableClass
        """
        # ------------------------------------------------------------ 01
        # get the possible field names that will be hashed
        setattr(
            self, Config.LITERAL.HASHABLE_FIELDS_LIST_KEY,
            [
                f.name for f in dataclasses.fields(self)
                if f.name not in ["hashable", "root_dir_str"]
            ]
        )

        # ------------------------------------------------------------ 02
        # if path exists load data dict from it
        if self.path.exists():
            _hashable_dict_from_disk = \
                m.FrozenDict.from_yaml(self.path.read_text())
            # update internal dict from HashableDict loaded from disk
            self.__dict__.update(
                _hashable_dict_from_disk.get()
            )

        # ------------------------------------------------------------ 03
        # now backup yaml str
        setattr(
            self,
            Config.LITERAL.BACKUP_YAML_STR_KEY,
            self.make_yaml_str_from_current_state(),
        )

        # ------------------------------------------------------------ 04
        # this locks future accesses
        setattr(self, Config.LITERAL.LOCK_ACCESS_FLAG, True)

    def __getattribute__(self, item):

        # bypass all dunder method accesses
        if item.startswith("__"):
            return super().__getattribute__(item)

        # note that the list is available only after __post_init__
        _hashable_fields = getattr(
            self, Config.LITERAL.HASHABLE_FIELDS_LIST_KEY, [])

        # if not a hashable field call super
        if item not in _hashable_fields:
            return super().__getattribute__(item)

        # check if there is no lock
        if hasattr(self, Config.LITERAL.LOCK_ACCESS_FLAG):
            e.code.CodingError(
                msgs=[
                    f"There is a lock on config state file ... to access "
                    f"fields in this class make sure to use the instance using "
                    f"`with` statement ...",
                    f"Error while access attribute `{item}`",
                ]
            )

        # call super and return
        return super().__getattribute__(item)

    def __setattr__(self, key, value):

        # bypass all dunder method accesses
        if key.startswith("__") and key.endswith("__"):
            return super().__setattr__(key, value)

        # note that the list is available only after __post_init__
        _hashable_fields = getattr(
            self, Config.LITERAL.HASHABLE_FIELDS_LIST_KEY, [])

        # if not a hashable field call super
        if key not in _hashable_fields:
            return super().__setattr__(key, value)

        # check if there is no lock
        if hasattr(self, Config.LITERAL.LOCK_ACCESS_FLAG):
            e.code.CodingError(
                msgs=[
                    f"There is a lock on config state file ... to access "
                    f"fields in this class make sure to use the instance using "
                    f"`with` statement ..."
                    f"Error while access attribute `{key}`",
                ]
            )

        # call super and return
        return super().__setattr__(key, value)

    def __del__(self):
        """
        todo: raising errors in __del__ will pollute logs ... but for now we
          keep this probable redundant code for extra check to test if we
          are syncing properly
        """

        with self():
            _backup_yaml_str = getattr(self, Config.LITERAL.BACKUP_YAML_STR_KEY)
            _current_yaml_str = self.make_yaml_str_from_current_state()
            if _backup_yaml_str != _current_yaml_str:
                e.code.CodingError(
                    msgs=[
                        f"You should make sure that you are using `with` "
                        f"statement while using config. Looks like you have "
                        f"updates hashable fields from outside with context.",
                        f"Also make sure that you are not nesting with "
                        f"statements",
                        {
                            "_backup_yaml_str": _backup_yaml_str,
                            "_current_yaml_str": _current_yaml_str
                        }
                    ]
                )

    def __call__(
        self, do_not_save: bool = False
    ) -> "Config":
        # noinspection PyTypeChecker
        return super().__call__(do_not_save=do_not_save)

    def on_enter(self) -> "Config":
        # call super
        super().on_enter()

        # get kwargs
        do_not_save: bool = self.internal.on_call_kwargs['do_not_save']

        # if do_not_save is True then we expect the config file not to be
        # present on disc ...
        if do_not_save:
            if self.path.is_file():
                e.code.CodingError(
                    msgs=[
                        f"You do not want to save any updates to config file "
                        f"as so_not_save=True",
                        f"In that case we expect that there should be no "
                        f"stale state present on disk as we assume you will "
                        f"sync config later ..."
                    ]
                )

        # we expect the lock to be always there
        if not hasattr(self, Config.LITERAL.LOCK_ACCESS_FLAG):
            e.code.CodingError(
                msgs=[
                    f"For config we expect the lock to be always there.",
                    f"Make sure you always use `with` statement to access or "
                    f"update fields of the config state file.",
                    f"Also check if you are nesting with statements as that "
                    f"will lead to same error."
                ]
            )

        # now remove lock so that we can access or update things
        delattr(self, Config.LITERAL.LOCK_ACCESS_FLAG)

        # check if serializable state is mutated outside with context
        _backup_yaml_str = getattr(self, Config.LITERAL.BACKUP_YAML_STR_KEY)
        _current_yaml_str = self.make_yaml_str_from_current_state()
        if _backup_yaml_str != _current_yaml_str:
            e.code.CodingError(
                msgs=[
                    f"You should make sure that you are using `with` "
                    f"statement while using config. Looks like you have "
                    f"updates hashable fields from outside with context.",
                    f"Also make sure that you are not nesting with statements",
                    {
                        "_backup_yaml_str": _backup_yaml_str,
                        "_current_yaml_str": _current_yaml_str
                    }
                ]
            )

        # return
        return self

    def on_exit(self):

        # get kwargs
        do_not_save: bool = self.internal.on_call_kwargs['do_not_save']

        # if something was changed inside with statement that it should not
        # match with backed up yaml str
        _backup_yaml_str = getattr(self, Config.LITERAL.BACKUP_YAML_STR_KEY)

        # now let us get current yaml str
        _current_yaml_str = self.make_yaml_str_from_current_state()

        # if something changed then call write to disk
        if _backup_yaml_str != _current_yaml_str:
            # before updating let us update the config_updated_on
            # this can never happen
            if len(self.config_updated_on) > \
                    self.LITERAL.config_updated_on_list_limit:
                e.code.CodingError(
                    msgs=[
                        f"This should never happens ... did you try to append "
                        f"last_updated_on list multiple times"
                    ]
                )
            # limit the list
            if len(self.config_updated_on) == \
                    self.LITERAL.config_updated_on_list_limit:
                self.config_updated_on = self.config_updated_on[1:]
            # append time
            self.config_updated_on.append(datetime.datetime.now())
            # after update to self.config_updated_on we need to generate
            # again new yaml str
            _current_yaml_str = self.make_yaml_str_from_current_state()
            # now write the updates
            if not do_not_save:
                self.path.write_text(_current_yaml_str)
            # also update the _backup_yaml_str
            setattr(self, Config.LITERAL.BACKUP_YAML_STR_KEY, _current_yaml_str)

        # since we are exiting put back the lock
        setattr(self, Config.LITERAL.LOCK_ACCESS_FLAG, True)

        # call super
        super().on_exit()

    def make_yaml_str_from_current_state(self) -> str:
        return m.FrozenDict(
            item={
                f: getattr(self, f)
                for f in getattr(self, Config.LITERAL.HASHABLE_FIELDS_LIST_KEY)
            }
        ).yaml()

    def sync(self):
        """
        Note that __enter__ and __exit__ will take care of always updating
        the state. SO instead here we will validate if state on disk matches
        our serializable.
        """
        # if no config file the update created_on and with statement will
        # sync and also add time stamp to config_update_on
        if not self.path.exists():
            # with statement helps in sync
            with self():
                # ... self.config.created_on must be None as created_on
                # can be only modified here
                if self.created_on is not None:
                    e.code.CodingError(
                        msgs=[
                            f"We expect this to be None as info file is not "
                            f"yet written to disk"
                        ]
                    )
                # ... update config to store info for when info file was created
                self.created_on = datetime.datetime.now()
        # else read the config and match it
        else:
            with self():
                _current_state = self.make_yaml_str_from_current_state()
                _disk_state = self.path.read_text()
                if _current_state != _disk_state:
                    e.code.CodingError(
                        msgs=[
                            f"We expect the state on disk to same to internal "
                            f"state for config",
                            {
                                "_current_state": _current_state,
                                "_disk_state": _disk_state
                            }
                        ]
                    )

    def delete(self):
        # delete associated file on the disk
        self.path.unlink()

        # also reset the config based on default values
        # this we achieve by creating new object on the fly ...
        # Note we can also wipe cache using
        # `util.WipeCacheResult("config", self.hashable)` but that will not
        # help as this object itself is cached
        # noinspection PyArgumentList
        _default_config = self.__class__(
            hashable=self.hashable, root_dir_str=self.root_dir_str
        )
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
        # just call sync
        # + if present will check the file on disk with internal state
        # + else will create file
        self.config.sync()
