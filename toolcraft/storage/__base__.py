"""
Holds the base classes for storage module.
These are special hashables whose state can be serialized on disk.
"""

import typing as t
import pathlib
import datetime
import dataclasses
import abc

from .. import util, logger, settings
from .. import marshalling as m
from .. import error as e
from . import state

_LOGGER = logger.get_logger()

_DOT_DOT_TYPE = t.Literal['..']
# noinspection PyUnresolvedReferences
_DOT_DOT = _DOT_DOT_TYPE.__args__[0]


class HashesDict(m.FrozenDict):

    @property
    def allowed_types(self) -> t.Tuple[t.Type]:
        return str,

    @property
    def allowed_nesting(self) -> bool:
        return False

    def __init__(
            self,
            item: t.Dict[str, str]
    ):

        # call super
        super().__init__(item=item)

        # validate - all values need to be string of len 64
        for k, v in item.items():
            if len(v) != 64:
                e.validation.NotAllowed(
                    msgs=[
                        f"The hashes dict must have a string value with "
                        f"length 64"
                    ]
                )

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!frozen_hashes_dict"


@dataclasses.dataclass
class StorageHashableConfig(state.Config):

    class LITERAL(state.Config.LITERAL):
        accessed_on_list_limit = 10

    # will be updated when File or Folder is accessed
    accessed_on: t.List[datetime.datetime] = dataclasses.field(
        default_factory=list
    )

    # noinspection DuplicatedCode
    def append_last_accessed_on(self):
        # this can never happen
        if len(self.accessed_on) > \
                self.LITERAL.accessed_on_list_limit:
            e.code.CodingError(
                msgs=[
                    f"This should never happens ... did you try to append "
                    f"last_accessed_on list multiple times"
                ]
            )
        # limit the list
        if len(self.accessed_on) == \
                self.LITERAL.accessed_on_list_limit:
            self.accessed_on = self.accessed_on[1:]
        # append time
        self.accessed_on.append(datetime.datetime.now())


class StorageHashableInternal(m.Internal):

    @property
    def owner(self) -> "StorageHashable":
        # noinspection PyTypeChecker
        return super().owner


@dataclasses.dataclass(frozen=True)
class StorageHashable(m.HashableClass, abc.ABC):

    parent_folder: t.Optional["Folder"]

    @property
    @util.CacheResult
    def config(self) -> StorageHashableConfig:
        return StorageHashableConfig(
            hashable=self,
            root_dir_str=self.root_dir.as_posix(),
        )

    @property
    @util.CacheResult
    def internal(self) -> "StorageHashableInternal":
        return StorageHashableInternal(self)

    @property
    def root_dir(self) -> pathlib.Path:
        # this property should never be called when parent_folder is None as
        # it will be overridden
        if self.parent_folder is None:
            e.code.ShouldNeverHappen(
                msgs=[
                    f"This is already validated in init_validate",
                    f"You are supposed to override property root_dir in class "
                    f"{self.__class__} if you are not supplying field "
                    f"parent_folder i.e. when parent_folder=None"
                ]
            )
            raise

        # If parent_folder is provided this property will not be overridden,
        # hence we will reach here.
        # In order to avoid creating Folder instance for parent_folder we use
        # `..` string while saving to disc. This makes sure that there is no
        # recursive instances of Folder being created. These instances again
        # tries to sync leading to recursion
        # But that means the Folder which is creating this instance must set
        # itself as parent_folder.
        # Also check documentation for `Folder.sync()` and
        # `StorageHashable.init_validate()`
        # Note in init_validate if self.parent_folder is `..` we raise error
        # stating that you are creating instance from yaml file directly and
        # it is not allowed as parent_folder should do it while syncing
        if self.parent_folder == _DOT_DOT:
            e.code.CodingError(
                msgs=[
                    f"Yaml on disc can have `..` string so the Folder which "
                    f"is creating this instance must update it and then call "
                    f"__post_init__ over the StorageHashable",
                    f"{Folder.sync} is responsible to set parent_folder while "
                    f"syncing.",
                    f"While in case if you are creating instance "
                    f"directly from yaml file then "
                    f"{StorageHashable.init_validate} should ideally block "
                    f"you as it is not possible to create instance.",
                    f"Also note that we do all this because hex_hash will be "
                    f"corrupt if parent_folder is not set appropriately "
                    f"before `Hashable.init` runs"
                ]
            )
            raise

        # Now if parent_folder is Folder simply return the path of
        # parent_folder as it is the root_dir for this StorageHashable
        if isinstance(self.parent_folder, Folder):
            return self.parent_folder.path

        # if above thing does not return that means we have a problem so
        # raise error
        e.code.CodingError(
            msgs=[
                f"The field parent_folder is not None nor it is valid "
                f"Folder",
                f"The type is {type(self.parent_folder)}"
            ]
        )
        raise

    @property
    def is_created(self) -> bool:
        return self.state_manager.is_available

    @property
    @util.CacheResult
    def state_manager(self) -> "state.StateManager":
        return state.StateManager(
            hashable=self,
            root_dir_str=self.root_dir.as_posix(),
            config=self.config
        )

    @classmethod
    def hook_up_methods(cls):
        # call super
        super().hook_up_methods()

        # hook up create
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.create,
            pre_method=cls.create_pre_runner,
            post_method=cls.create_post_runner,
        )

        # hook up delete
        util.HookUp(
            cls=cls,
            silent=True,
            method=cls.delete,
            pre_method=cls.delete_pre_runner,
            post_method=cls.delete_post_runner,
        )

    def init_validate(self):
        # ----------------------------------------------------------- 01
        # If parent_folder is provided this property will not be overridden,
        # hence we will reach here.
        # In order to avoid creating Folder instance for parent_folder we use
        # `..` string while saving to disc. This makes sure that there is no
        # recursive instances of Folder being created. These instances again
        # tries to sync leading to recursion
        # But that means the Folder which is creating this instance must set
        # itself as parent_folder.
        # Also check documentation for `Folder.sync()` and
        # `StorageHashable.init_validate()`
        # Note in init_validate if self.parent_folder is `..` we raise error
        # stating that you are creating instance from yaml file directly and
        # it is not allowed as parent_folder should do it while syncing
        if self.parent_folder == _DOT_DOT:
            e.code.CodingError(
                msgs=[
                    f"Problem with initializing {self.__class__}",
                    f"Yaml on disc can have `..` string so the Folder which "
                    f"is creating this instance must update it and then call "
                    f"__post_init__ over the StorageHashable",
                    f"{Folder.sync} is responsible to set parent_folder while "
                    f"syncing.",
                    f"While in case if you are creating instance "
                    f"directly from yaml file then "
                    f"{StorageHashable.init_validate} should ideally block "
                    f"you as it is not possible to create instance.",
                    f"Also note that we do all this because hex_hash will be "
                    f"corrupt if parent_folder is not set appropriately "
                    f"before `Hashable.init` runs"
                ]
            )
            raise

        # ----------------------------------------------------------- 02
        # call super
        super().init_validate()

        # ----------------------------------------------------------- 03
        # validate root_dir and hence parent_folder
        # Note that if parent_folder is not supplied then root_dir must be
        # overridden
        _ = self.root_dir

        # ----------------------------------------------------------- 04
        # check for root_dir length
        e.io.LongPath(path=self.root_dir, msgs=[])

        # if root_dir exists check if it is a folder
        if self.root_dir.exists():
            if not self.root_dir.is_dir():
                e.validation.NotAllowed(
                    msgs=[
                        f"We expect {self.root_dir} to be a dir"
                    ]
                )

        # ----------------------------------------------------------- 05
        # wither you override root_dir or else you supply parent_folder
        _parent_folder_supplied = self.parent_folder is not None
        _root_dir_overridden = \
            self.__class__.root_dir != StorageHashable.root_dir
        if not (_parent_folder_supplied ^ _root_dir_overridden):
            e.code.CodingError(
                msgs=[
                    f"For subclasses of Folder you either need to supply "
                    f"parent_folder or else override property root_dir",
                    f"For instances of class {self.__class__} we found that "
                    f"you: ",
                    {
                        "supplied parent_folder": _parent_folder_supplied,
                        "overrided root_dir property": _root_dir_overridden,
                    }
                ]
            )

        # ----------------------------------------------------------- 06
        # if parent_folder supplied check what it can contain
        if self.parent_folder is not None:
            if self.parent_folder.contains is None:
                e.code.NotAllowed(
                    msgs=[
                        f"The parent_folder is configured to contain arbitrary "
                        f"things i.e. parent_folder.contains is None",
                        f"So may be you might not be intending to add instance "
                        f"of class {self.__class__} to parent_folder of type "
                        f"{self.parent_folder.__class__}"
                    ]
                )
            # else the parent_folder wants to track specific things
            else:
                # note we do not use isinstance() as all folder
                # subclasses will be concrete and subclassing is not anything
                # special as there is no hierarchy in folder types
                if self.__class__ != self.parent_folder.contains:
                    e.code.NotAllowed(
                        msgs=[
                            f"The parent_folder is configured to contain only "
                            f"instances of class "
                            f"{self.parent_folder.contains} but you "
                            f"are trying to add instance of type "
                            f"{self.__class__}"
                        ]
                    )

    def init(self):
        # call super
        super().init()

        # if root dir does not exist make it
        if not self.root_dir.exists():
            self.root_dir.mkdir(parents=True)

        # if not created create
        if not self.is_created:
            self.create()

        # if has parent_folder add self to items
        if self.parent_folder is not None:
            # add item ... note if item already exists due to sync we will
            # overwrite it
            self.parent_folder.add_item(hashable=self)

    def as_dict(
        self
    ) -> t.Dict[str, m.SUPPORTED_HASHABLE_OBJECTS_TYPE]:
        # get dict from super
        _dict = super().as_dict()

        # if there is parent_folder update it to ..
        if self.parent_folder == _DOT_DOT:
            e.code.CodingError(
                msgs=[
                    f"If loading from yaml on disk make sure that a Folder is "
                    f"doing that un sync so that parent_folder is set "
                    f"appropriately before calling __post_init__ on "
                    f"StorageHashable"
                ]
            )

        # modify dict so that representation is change on disc
        # note that this does not modify self.__dict__ ;)
        # we do this only when parent_folder is available
        if self.parent_folder is not None:
            _dict['parent_folder'] = _DOT_DOT

        # return
        return _dict

    @classmethod
    def from_dict(
        cls,
        yaml_state: t.Dict[str, "m.SUPPORTED_HASHABLE_OBJECTS_TYPE"],
        **kwargs
    ) -> "StorageHashable":
        # update .. to parent_folder supplied from kwargs
        if yaml_state["parent_folder"] == _DOT_DOT:
            if "parent_folder" not in kwargs.keys():
                e.code.CodingError(
                    msgs=[
                        f"The yaml_state dict loaded from file_or_text does "
                        f"has parent_folder set to `..`",
                        f"This means we do not have access to parent_folder "
                        f"instance so please supply it while Folder syncs "
                        f"files/folders inside it.",
                        f"Note that if you are using from_yaml then also you "
                        f"can supply the extra kwarg so that from|_dict "
                        f"receives it."
                    ]
                )
            else:
                yaml_state["parent_folder"] = kwargs["parent_folder"]

        # noinspection PyArgumentList
        return cls(**yaml_state)

    def create_pre_runner(self):
        # check if already created
        if self.is_created:
            e.code.NotAllowed(
                msgs=[
                    f"Things related to hashable class {self.__class__} "
                    f"with name `{self.name}` has already been created ...",
                ]
            )

    def create(self) -> t.Any:
        e.code.CodingError(
            msgs=[
                f"There is nothing to create for class {self.__class__}",
                F"You might need to override this method if you have "
                F"something to create ...",
                f"If you override this method make sure you override "
                f"corresponding `delete()` too ..."
            ]
        )

    # noinspection PyUnusedLocal
    def create_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):

        # ----------------------------------------------------------- 01
        # The below call will create state manager files on the disk
        # check if .info and .config file exists i.e. state exists
        if self.config.path.exists():
            e.code.CodingError(
                msgs=[
                    f"Looks like you have updated config before this parent "
                    f"create_post_runner was called.",
                    f"Try to make updates to config after the config is "
                    f"created the parent create_post_runner by calling sync()"
                ]
            )
        if self.state_manager.is_available:
            e.code.CodingError(
                msgs=[
                    f"We just finished creation for {self.__class__} and "
                    f"wanted to create files related to state manager",
                    f"But we already found them on disk for {self.name!r}"
                ]
            )
        # the file were created now .... so update state accordingly
        self.state_manager.sync_to_disk()

        # ----------------------------------------------------------- 02
        # if config.DEBUG_HASHABLE_STATE we will create files two times
        # to confirm if states are consistent and hence it will help us to
        # de DEBUG_HASHABLE_STATE
        # The logic is:
        # 01: if: current state available
        #   + ...
        # 02: else: current state not available
        #   02.01: create current state
        #   02.02: if config.DEBUG_HASHABLE_STATE:
        #          > if: backup state is available (2nd pass)
        #            - compare current state with backup state
        #          > else: if backup state is not available (1st pass)
        #            - create backup state from current state
        #            - delete current state, and the things created by
        #              parent
        #            - make sure that delete above create files again as
        #              we cannot create things for `parent hashable` here
        # Note that this part of code (i.e. 02.xx) will never get called
        # after 2 passes are over as both backup state and current state
        # will be on the disk
        if settings.FileHash.DEBUG_HASHABLE_STATE:
            _state_manager = self.state_manager
            if _state_manager.is_backup_available:

                # get backup state info on disk
                _backup_info = self.from_yaml(
                    _state_manager.info.backup_path,
                    bypass_post_init_call=True
                )
                _current_info = self

                # crosscheck all fields
                _mismatched_fields = {}
                for f_name in _current_info.dataclass_field_names:

                    # compare
                    _backup_v = getattr(_backup_info, f_name)
                    _current_v = getattr(_current_info, f_name)
                    if _backup_v != _current_v:
                        _mismatched_fields[f_name] = {
                            "current": _current_v,
                            "backup": _backup_v
                        }

                # raise if mismatch happened
                if bool(_mismatched_fields):
                    e.code.CodingError(
                        msgs=[
                            f"*** ******************************** ***",
                            f"*** YOU ARE DEBUGGING HASHABLE STATE ***",
                            f"*** ******************************** ***",
                            f"We found discrepancy in "
                            f"{_state_manager.info.path.name!r} "
                            f"from root dir "
                            f"{_state_manager.root_dir_str}.",
                            f"This happens when data generation code has "
                            f"generated different data. Make sure that if "
                            f"you use randomness it must be deterministic.",
                            f"The below fields do not match:",
                            _mismatched_fields,
                            f"*** ******************************** ***",
                            f"*** ********** END DEBUG *********** ***",
                            f"*** ******************************** ***",
                        ]
                    )
            else:
                # create backup
                _state_manager.info.backup_path.write_text(self.yaml())
                # lock them up (note both info and config are locked)
                util.io_make_path_read_only(
                    _state_manager.info.backup_path)
                # delete things created by hashable parent note that this
                # should also delete files related to state manager
                self.delete()
                # now let's create again both the things for hashable and
                # the state manager files
                self.create()

        # ----------------------------------------------------------- 03
        # check if property updated
        if not self.is_created:
            e.code.NotAllowed(
                msgs=[
                    f"Did you forget to update appropriately the things in "
                    f"`create()` method of {self.__class__}",
                    f"Property `self.is_created` should return `True` as "
                    f"things are now created."
                ]
            )

    # noinspection PyUnusedLocal
    def delete_pre_runner(self, *, force: bool = False):
        # check if already created
        if not self.is_created:
            e.code.NotAllowed(
                msgs=[
                    f"Things related to hashable class {self.__class__} are "
                    f"not created ..."
                ]
            )

    def delete(self, *, force: bool = False) -> t.Any:
        e.code.CodingError(
            msgs=[
                f"There is nothing to delete for class {self.__class__}",
                F"You might need to override this method if you have "
                F"something to delete ...",
                f"You only `delete()` if you create something in `create()`"
            ]
        )

    # noinspection PyUnusedLocal
    def delete_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        # delete state manager files as they were created along with teh
        # files for this StorageHashable in create_post_runner
        self.state_manager.delete()

        # check if property updated
        if self.is_created:
            e.code.NotAllowed(
                msgs=[
                    f"Did you forget to update appropriately the things in "
                    f"`delete()` method of {self.__class__}",
                    f"Property `self.is_created` should return `False` as "
                    f"things are now deleted."
                ]
            )

        # if parent_folder is there try to remove item from the tracking dict
        # items
        if self.parent_folder is not None:
            # just do sanity check if we are having same item
            if id(self) != id(self.parent_folder.items[self.name]):
                e.code.CodingError(
                    msgs=[
                        f"We expect these objects to be same ... "
                        f"make sure to add item using "
                        f"parent_folder.add_item() method for integrity"
                    ]
                )
            # in init() we added self by calling
            # self.parent_folder.add_item(self) ... now we just remove the
            # item from tracking dict items so that parent folder is in sync
            del self.parent_folder.items[self.name]

        # now we have removed strong reference to self in parent_folder.items
        # dict ... let us make this instance useless as files are deleted
        # hence we want to make sure any other references will fail to use
        # this instance ...
        # To achieve this we just clear out the internal __dict__
        self.__dict__.clear()


@dataclasses.dataclass(frozen=True)
class Folder(StorageHashable):
    """
    A folder for hashable instance like Dataset or Model.

    Name of the folder:
      The name of folder is the name of the hashable it represents. The
      dataclass field `for_hashable` signifies the uniqueness of the folder
      while the `paren_folder` field super class does not affect uniqueness
      as the folder represented by this class is saved under it ;)

      Deviation from `HashableClass.name` behaviour:
        You might be thinking why not have have folder hex_hash as folder name.
        That sounds fine. But the name of folder using hashables name can in
        future let us use via external utilities to pick up folders only by
        knowing hashable and the root_dir must be provided only once.
        Also parent_folder is required only to get parent folder info we can
        get away just by knowing the path.

      Note that for FileGroup the parent_folder is considered as they have
      even more fields and here we ignore parent_folder so that for_hashable
      decides the folder name

    We do not allow to add fields in subclass:
      In order that *.info files do not pollute with more info we do not
      allow to add fields to Folder class while subclassing.
      In case you want more info please use *.config file via Folder.config
      property

    The contains property:
      Indicates what will stored in this Folder

    When parent_folder is None override root_dir
      This behaviour is borrowed from super class and well suits the
      requirement for Folder class

    Made up of three things
    + <hash>.info
      - when loaded gives out Folder object with hashable instance object
    + <hash>.config
      - the access info
    + <hash> folder
      - A folder inside which you can have folder's or file_group's
    """
    for_hashable: t.Union[str, m.HashableClass]

    @property
    def name(self) -> str:
        """
        Do not override.

        NOTE this also happens to be name of the folder which will be
        created inside root_dir

        Note that for Folder the uniqueness is completely decided by
        self.for_hashable field.

        If self.for_hashable is str then the user is not using hashable and
        simply wants to create folder with some specific name

        We use self.for_hashable.name as name of the folder. Remember that
        name is to be unique across hashable. By default the name returns
        hex_hash but when you override it to return string the user need to
        take care that it is unique for each instance of that class.

        Note that FileGroup considers parent_folder while creating name but
        here we ignore as there are no extra fields we will define here. Also
        we want fo_hashable to dictate things in Folder like the name of
        folder created on disk.
        """

        # the name is dictated by for_hashable as we will not allow any
        # fields in Folder (check validation)
        # This is unlike FileGroup where all fields decide name ... this si
        # because in FileGroup we intend to have more fields
        if isinstance(self.for_hashable, str):
            return self.for_hashable
        else:
            # the name defaults to hex_hash but if you have overridden it then
            # we assume you have taken care of creating unique name for all
            # possible instance of hashable class
            return self.for_hashable.name

    @property
    @util.CacheResult
    def path(self) -> pathlib.Path:
        return self.root_dir / self.name

    @property
    def is_created(self) -> bool:
        """
        This does mean we need call to create_all

        todo: maybe not that big of a overhead but try to check if call to
          this property is minimal
        """

        # ----------------------------------------------------------------01
        _folder_present = self.path.is_dir()
        # (The super method is responsible to do this as state manager is
        # available)
        _state_manager_files_available = super().is_created

        # ----------------------------------------------------------------02
        # if _state_manager_files_available then folder must be present... the
        # vice versa is not necessary ... this is because when state manager
        # files are deleted we might still retain Folders as they hold
        # valuable files like download files, processed files, results etc.
        # NOTE: we do delete state files in cases when config and info files
        # are are modifies over new versions ... so we need to protect data
        # deletion
        if _state_manager_files_available:
            if not _folder_present:
                e.code.CodingError(
                    msgs=[
                        f"The state is available but respective folder is "
                        f"absent."
                    ]
                )

        # ----------------------------------------------------------------03
        # time to return
        return _state_manager_files_available

    @property
    def contains(self) -> t.Optional[t.Type[StorageHashable]]:
        """
        todo: for contains and read_only we can have a class decorator for
          Folder like StoreField ... although that means we need to avoid
          subclassing the Folder decorator ... but can figure it out later
        Indicates what this folder should contain ... it can be one of Folder
        or FileGroup or None (i.e. Files that will not use auto hashing
        mechanism)

        Default is None that means we have files whose hash is not tested ...
        in that case we also will not have state manager files like
        *.info and *.hash
        """
        return None

    @property
    @util.CacheResult
    def items(self) -> util.SmartDict:
        if self.contains is None:
            e.code.CodingError(
                msgs=[
                    f"You have set contains to None so we do not know what "
                    f"will be stored .... so ideally you will never track "
                    f"things in the folder so you should not be using this "
                    f"property .... check class {self.__class__}"
                ]
            )
        return util.SmartDict(
            allow_nested_dict_or_list=False,
            supplied_items=None,
            use_specific_class=self.contains,
        )

    @classmethod
    def block_fields_in_subclasses(cls) -> bool:
        return True

    def init_validate(self):

        # -----------------------------------------------------------------01
        # call super
        super().init_validate()

        # -----------------------------------------------------------------02
        # check if path is dir
        if self.path.exists():
            if not self.path.is_dir():
                e.code.CodingError(
                    msgs=[
                        f"Found {self.path} which is not a dir ..."
                    ]
                )

        # -----------------------------------------------------------------03
        # Want to check if there is garbage in folder
        # don't be tempted to do this check as ,,,, sync also does not do
        # that .... check method `warn_about_garbage` and we should do that
        # in standalone mode not while instance are getting created
        # ;) ;) ;)
        #   PLEASE DONT BE TEMPTED TO CHECK WHAT IT CONTAINS IN SYNC METHOD

    def init(self):
        # call super
        super().init()

        # this is like `get()` for Folder .... note that all
        # FileGroups/Folders will be added here via add_item
        if self.contains is not None:
            self.sync()

    def create(self) -> pathlib.Path:
        """
        If there is no Folder we create an empty folder.
        """
        if not self.path.is_dir():
            self.path.mkdir()

        # return
        return self.path

    def delete(self, *, force: bool = False):
        """
        Deletes Folder.

        Note: Do not do read_only check here as done in delete_item method as
        it is not applicable here and completely depends on parent folder
        permissions

        Note we delete only empty folders, and the state ... we will not
        support deleting non-empty folders

        note: force kwarg does not matter for a folder but just kept alongside
        FileGroup.delete for generic behaviour

        todo: when `self.contains is None` handle delete differently as we
          will not have items dict
        """

        # todo: do u want to add permission check for
        #  Folder similar to FileGroup
        # when contains is None we delete everything ... this is default
        # behaviour if you want to do something special please override this
        # method
        if self.contains is None:
            # note that this will also delete folder self.path
            util.pathlib_rmtree(path=self.path, recursive=True, force=False)
            # remember to make empty dir as per API
            self.path.mkdir(exist_ok=True)
        # else since the folder can track items delete them using items and
        # calling the respective delete of items
        else:
            _items = self.items.keys()
            for item in _items:
                # first delete the item physically
                self.items[item].delete(force=force)

        # todo: remove redundant check
        # by now we are confident that folder is empty so just check it
        if not util.io_is_dir_empty(self.path):
            e.code.CodingError(
                msgs=[
                    f"The folder should be empty by now ...",
                    f"Check path {self.path}"
                ]
            )

        # since we are deleting everything here do not forget to delete the
        # resulting parent empty folder
        self.path.rmdir()

    def warn_about_garbage(self):
        """

        In sync() we skip anything that does not end with *.info this will also
        skip files that are not StorageHashable .... but that is okay for
        multiple reasons ...
         + performance
         + we might want something extra lying around in folders
         + we might have deleted state info but the folders might be
           lying around and might be wise to not delete it
        The max we can do in that case is warn users that some
        thing else is lying around in folder check method
        warn_about_garbage.

        todo: implement this

        """
        ...

    def sync(self):
        """
        Sync is heavy weight call rarely we aim to do all validations here
        and avoid any more validations later ON ...

        todo: We can have special Config class for Folder which can do some
          indexing operation
        """

        # -----------------------------------------------------------------01
        # Validations
        if self.contains is None:
            e.code.CodingError(
                msgs=[
                    f"The caller code should take care to check if there is "
                    f"anything trackable inside this Folder",
                    f"Property contains is None so do not call sync"
                ]
            )
        # tracking dict should be empty
        if len(self.items) != 0:
            e.code.CodingError(
                msgs=[
                    f"We expect that the tracker dict be empty",
                    f"Make sure that you are calling sync only once i.e. from "
                    f"__post_init__"
                ]
            )

        # -----------------------------------------------------------------02
        # track for registered file groups
        for f in self.path.iterdir():
            # *** NOTE ***
            # We skip anything that does not end with *.info this will also
            # skip files that are not StorageHashable .... but that is okay
            # for multiple reasons ...
            #  + performance
            #  + we might want something extra lying around in folders
            #  + we might have deleted state info but the folders might be
            #    lying around and might be wise to not delete it
            # The max we can do in that case is warn users that some
            # thing else is lying around in folder check method
            # warn_about_garbage.

            # registered items have metainfo file with them
            # only consider if meta info file exists
            if not f.name.endswith(state.Suffix.info):
                continue

            # if self.contains is None the Folder was configured too not have
            # FileGroup or Folder .... so it should not have any *.info files
            # and can have anything else like arrow storage files etc
            # Note that if we reach here the file in question is *.info file
            # so we do not want contains=None in that case
            if self.contains is None:
                e.code.CodingError(
                    msgs=[
                        f"We found a file {f} which is hashable info file",
                        f"Since the folder {self.__class__} was configured to "
                        f"have no {StorageHashable} instances, we will "
                        f"raise error.",
                        f"As we do not expect a *.info file."
                    ]
                )

            # construct hashable instance from meta file
            # Note that when instance for hashable is created it will check
            # things on its own periodically
            # Note the __post_init__ call will also sync things if it is folder
            # noinspection PyTypeChecker
            _hashable = self.contains.from_yaml(
                f, parent_folder=self,
            )  # type: StorageHashable

            # add tuple for tracking
            # todo: no longer needed to add here as when we create instance
            #  the instance adds itself to parent_folder instance ... delete
            #  this code later ... kept for now just for reference
            # noinspection PyTypeChecker
            # self.items[_hashable.name] = _hashable

        # -----------------------------------------------------------------03
        # sync is equivalent to accessing folder
        # so update state manager files
        self.config.append_last_accessed_on()

    def add_item(self, hashable: StorageHashable):

        # since we are adding hashable item that are persisted to disk their
        # state should be present on disk
        if not hashable.state_manager.is_available:

            # err msg
            if isinstance(hashable, StorageHashable):
                _err_msg = f"This should never happen for " \
                           f"{hashable.__class__} " \
                           f"sub-class, there might be some coding error." \
                           f"Did you forget to call create file/folder " \
                           f"before adding the item."
                e.code.CodingError(
                    msgs=[
                        f"We cannot find the state for the following hashable "
                        f"item on disk",
                        hashable.yaml(), _err_msg,
                    ]
                )
            else:
                _err_msg = f"Don't know the type {type(hashable)}"
                e.code.ShouldNeverHappen(msgs=[_err_msg])

        # Note due to sync that gets called when parent_folder instance
        # was created the items dict of parent_folder will get instance
        # of self if already present on disc ... in that case delete the
        # item in dict and replace with self ...
        if hashable.name in self.items.keys():
            # Also we do sanity check for integrity to check if hash of
            # existing item matches hashable ... this ensure that this is
            # safe update of dict
            if hashable.hex_hash != self.items[hashable.name].hex_hash:
                e.code.NotAllowed(
                    msgs=[
                        f"While syncing from disk the hashable had different "
                        f"hex_hash than one assigned now",
                        f"We expect that while creating objects of "
                        f"StorageHashable it should match with hex_hash of "
                        f"equivalent object that was instantiated from disk",
                        {
                            "yaml_on_dsk": self.items[hashable.name].yaml(),
                            "yaml_in_memory": hashable.yaml(),
                        }
                    ]
                )
            # note we do not call delete() method of  item as it will delete
            # actual files/folder on disc
            # here we just update dict
            del self.items[hashable.name]

        # add item
        self.items[hashable.name] = hashable
