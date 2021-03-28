"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import typing as t
from dearpygui import core as dpgc
from dearpygui import simple as dpgs
import numpy as np
import enum

from .. import error as e
from .. import logger
from .. import util

_LOGGER = logger.get_logger()

MANDATORY = "__IT_IS_MANDATORY__"


class _ReadOnlyClass(type):
    def __setattr__(self, key, value):
        e.code.NotAllowed(
            msgs=[
                f"Class {self} is read only.",
                f"You cannot override its attribute {key!r} programmatically.",
                f"Edit it during class definition ..."
            ]
        )


@dataclasses.dataclass(frozen=True)
class _Builder(abc.ABC):

    class LITERAL(metaclass=_ReadOnlyClass):

        def __new__(cls, *args, **kwargs):
            e.code.NotAllowed(
                msgs=[
                    f"This class is meant to be used to hold class "
                    f"variables only",
                    f"Do not try to create instance of {cls} ..."
                ]
            )

    def __post_init__(self):

        self.init_validate()

        self.init()

    def init_validate(self):
        ...

    def init(self):
        ...


@dataclasses.dataclass(frozen=True)
class _WidgetInternal:
    name: str
    parent: t.Union["Dashboard", "Widget"]

    @property
    def id(self) -> str:
        return f"{self.parent.id}.{self.name}"


class Color(enum.Enum):
    DEFAULT = enum.auto()
    WHITE = enum.auto()
    BLACK = enum.auto()
    CUSTOM = enum.auto()

    @property
    def dpg_value(self) -> t.List[float]:
        if self is self.DEFAULT:
            return [0., 0., 0., -1.]
        elif self is self.WHITE:
            return [255., 255., 255., 255.]
        elif self is self.BLACK:
            return [0., 0., 0., 255.]
        elif self is self.CUSTOM:
            e.code.CodingError(
                msgs=[
                    f"Seems like you are using custom color in that case "
                    f"please pass [r, g, b, a] kwargs i.e. Color.CUSTOM(...)"
                ]
            )
        else:
            e.code.NotSupported(
                msgs=[f"Unknown {self}"]
            )

    # noinspection PyPep8Naming
    def __call__(self, r: float, g: float, b: float, a: float) -> "Color":
        """
        This method return fake Color when called with Color.CUSTOM(...)
        """
        if self is self.CUSTOM:
            class _:
                ...
            __ = _()
            __.dpg_value = [r, g, b, a]
            # noinspection PyTypeChecker
            return __
        else:
            e.code.CodingError(
                msgs=[
                    f"You are allowed to pass custom values only with "
                    f"{self.CUSTOM} color."
                ]
            )


@dataclasses.dataclass(frozen=True)
class Widget(_Builder, abc.ABC):

    class LITERAL(_Builder.LITERAL):
        internal = "internal"

    items: t.Optional[t.List["Widget"]] = None

    @property
    def id(self) -> str:
        return self.internal.id

    @property
    def parent_id(self) -> str:
        return self.internal.parent.id

    @property
    def used_as_container(self) -> bool:
        # default behaviour is to have any widget work for both options
        return self.items is not None

    @property
    @util.CacheResult
    def children(self) -> t.Dict[str, "Widget"]:
        """
        children are those dataclass fields that are also instance of class
        `Widget`
        """
        # ---------------------------------------------------- 01
        # _children_from_fields
        # container
        _children_from_fields = {}
        # loop over
        for f in dataclasses.fields(self):
            # get value for each field
            v = getattr(self, f.name)
            # never have Dashboard as a child
            if isinstance(v, Dashboard):
                e.code.CodingError(
                    msgs=[
                        f"{Dashboard} is never meant to be used as "
                        f"a child. Avoid using it as dataclass field"
                    ]
                )
            # check if it is widget and make it children
            if isinstance(v, Widget):
                # append
                _children_from_fields[f.name] = v
            # rest all values are ignored ... you can use them as instance
            # values for any reason ... only widgets are tracked and laid out
            # in UI
            ...

        # ---------------------------------------------------- 02
        # _children_from_items
        _children_from_items = {}
        if bool(self.items):
            for i, v in enumerate(self.items):
                _children_from_items[f"item[{i}]"] = v

        # ---------------------------------------------------- 03
        # if used_as_container check if children come only from items
        if self.used_as_container:
            if bool(_children_from_fields):
                e.code.CodingError(
                    msgs=[
                        f"Class {self.__class__} is configured to be used as "
                        f"container. So please supply widgets using "
                        f"field `items`",
                        f"Please refrain from adding fields to class that "
                        f"will use widgets."
                    ]
                )
        else:
            if bool(_children_from_items):
                e.code.CodingError(
                    msgs=[
                        f"Class {self.__class__} is configured not to be used "
                        f"as container. So please do not supply widgets using "
                        f"field `items`",
                        f"Please use dataclass fields instead to add the "
                        f"Widgets that you like to render."
                    ]
                )

        # ---------------------------------------------------- 03
        # both cannot be present either one or None should be present
        if bool(_children_from_fields) and bool(_children_from_items):
            e.code.CodingError(
                msgs=[
                    f"Looks like for class {self.__class__} widgets are "
                    f"provided both via items as well as dataclass fields",
                    f"This should never happen"
                ]
            )
        else:
            return {
                **_children_from_fields, **_children_from_items
            }

    @property
    @util.CacheResult
    def internal(self) -> _WidgetInternal:
        if self.LITERAL.internal in self.__dict__.keys():
            return self.__dict__[self.LITERAL.internal]
        else:
            e.code.CodingError(
                msgs=[
                    f"the method {self.set_internal} needs to be called before "
                    f"accessing property `internal`"
                ]
            )

    def init_validate(self):
        # call super
        super().init_validate()

        # if used as container check if items supplied
        if self.used_as_container:
            if self.items is None:
                e.validation.NotAllowed(
                    msgs=[
                        f"Class {self.__class__} is configured to be used as "
                        f"container so please supply widgets using items field"
                    ]
                )

        # check if mandatory values supplied
        for f in dataclasses.fields(self):
            v = getattr(self, f.name)
            if not isinstance(v, np.ndarray) and v == MANDATORY:
                e.code.NotAllowed(
                    msgs=[
                        f"Please supply value for field "
                        f"{f.name} while creating instance of class "
                        f"{self.__class__}"
                    ]
                )

    def init(self):

        # call super
        super().init()

        # every self will assign itself as parent for all its children i.e.
        # dataclass fields of this class which are instance of class Widget
        for k, c in self.children.items():
            c.set_internal(
                internal=_WidgetInternal(name=k, parent=self)
            )

    def set_internal(self, internal: _WidgetInternal):
        if self.LITERAL.internal in self.__dict__.keys():
            e.code.CodingError(
                msgs=[
                    f"internal was already set for widget {self}",
                    f"We expect the set_internal to be called only once during "
                    f"the lifetime of the program."
                ]
            )
        else:
            self.__dict__[self.LITERAL.internal] = internal

    @abc.abstractmethod
    def make_gui(self):
        ...

    def make_children_gui(self):
        # make gui for all children
        for k, c in self.children.items():
            c.make_gui()

    def preview(self):
        """
        You can see the preview of this widget without adding it to dashboard
        """
        _dash = Dashboard(
            name="PREVIEW",
            label=f"{self.__module__}:{self.__class__.__name__}",
            items=[self],
        )
        _dash.make_gui()
        _dash.run_gui()


@dataclasses.dataclass(frozen=True)
class Dashboard(Widget):
    """
    Dashboard is nothing but window.

    Note that `widget.Window` will be any window that will be inside the UI

    Refer:
    >>> dpgs.window

    Here we will take care of things like
    + screen resolution
    + theme
    + closing even handlers
    + favicon
    + login mechanism

    Note that we make this as primary window when we start GUI
    """

    name: str = MANDATORY
    label: str = ""

    @property
    def id(self) -> str:
        # for dashboard there is no parent so we have attribute name that
        # will be the id of super parent
        return self.name

    # noinspection PyPropertyDefinition,PyTypeChecker
    @property
    def parent_id(self) -> str:
        e.code.CodingError(
            msgs=[
                f"Do not use this property for Dashboard as there exists no "
                f"parent for it ..."
            ]
        )

    def make_gui(self):
        with dpgs.window(
            name=self.id,
            label=self.label,
            on_close=self.on_close,
        ):
            # -------------------------------------------------- 01
            # set the things for primary window
            # dpgc.set_main_window_size(550, 550)
            # dpgc.set_main_window_resizable(False)
            _title = self.name
            if self.label != "":
                _title += f" - {self.label}"
            dpgc.set_main_window_title(_title)

            # -------------------------------------------------- 02
            # make gui for all children
            self.make_children_gui()

    def run_gui(self):
        # make gui
        self.make_gui()
        # dpgc.start_dearpygui()
        dpgc.start_dearpygui(primary_window=self.id)

    def on_close(self, sender, data):
        dpgc.delete_item(self.id)
