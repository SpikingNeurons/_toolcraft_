"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import typing as t
from dearpygui import core as dpg
import numpy as np
import enum

from .. import error as e
from .. import logger
from .. import util
from .. import marshalling as m

if False:
    from . import Window

_LOGGER = logger.get_logger()

MANDATORY = "__IT_IS_MANDATORY__"


class Color(m.FrozenEnum, enum.Enum):
    DEFAULT = enum.auto()
    WHITE = enum.auto()
    BLACK = enum.auto()
    CUSTOM = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_color"

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


class WidgetInternal(m.Internal):
    name: str
    parent: t.Union["Dashboard", "Widget"]
    before: t.Optional["Widget"] = None
    is_build_done: bool = False

    @property
    @util.CacheResult
    def id(self) -> str:
        return f"{self.parent.id}.{self.name}"

    @property
    def dpg_kwargs(self) -> t.Dict[str, t.Any]:
        return dict(
            name=self.id,
            parent=self.parent.id,
            before="" if self.before is None else self.before.id
        )

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + \
               ['before', 'is_build_done', ]


@dataclasses.dataclass(frozen=True)
class Widget(m.HashableClass, abc.ABC):

    @property
    def id(self) -> str:
        return self.internal.id

    @property
    def parent(self) -> "Widget":
        return self.internal.parent

    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        return WidgetInternal(owner=self)

    @property
    @abc.abstractmethod
    def is_container(self) -> bool:
        """
        If the dpg component needs a call to end
        Needed when the component is container and is used in with context
        Tou figure out which component is container refer to
        >>> from dearpygui import simple
        And check which methods decorated with `#contextmanager` are making
        call to `end()`
        """
        ...

    @property
    def dashboard(self) -> "Dashboard":
        """
        This recursively gets to root and gets dashboard ... unnecessarily
          expensive
        todo: can we do set_data and get_data from dpg to access this
          Or is there a global attribute to fetch this info ??
        """
        return self.parent.dashboard

    @property
    @util.CacheResult
    def children(self) -> t.Dict[str, "Widget"]:
        # this will be populated when add_child is called
        return {}

    def __getattribute__(self, item):
        """
        Here we trick dataclass to treat Widgets that were assigned as
        default to be treated as non mutable ... this helps us avoid using
        default_factory
        """

        # bypass all dunder method accesses
        if item.startswith("__"):
            return super().__getattribute__(item)

        # first lets get value
        v = super().__getattribute__(item)

        # if item not a field name return as it is
        if item not in self.__dataclass_fields__.keys():
            return v

        # if not widget return as it is
        if not isinstance(v, Widget):
            return v

        # get the Field for this item
        _field = self.__dataclass_fields__[item]

        # get default value
        _field_value = _field.default

        # if default is MISSING that means the value was supplied via
        # constructor do the user will expect it to mutate
        if _field_value == dataclasses.MISSING:
            return v

        # if _field_value and v are same that means we still have not tricked
        # dataclass and this is the first time things are called so update
        # __dict__ here
        if id(_field_value) == id(v):
            v = v.copy()
            self.__dict__[item] = v
            return v
        # things are already update for this self so return as it is
        else:
            return v

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

    def copy(self) -> "Widget":
        """
        Note that Widgets can have widgets. Also widgets are mutable object.
        We want default_factory so that the Widget when used with other
        parent Widget make its copy and remains immutable when the instance
        is shared across different widgets.

        This simple allows us to avoid using default_factory option of
        `dataclass.Field` while building UI.

        We need this behaviour as we have internal property that needs to
        have different info when Widget is used in different places. Also we
        really do not want to send extra info i.e. `self.id` and
        `self.parent_id` to update and add Ui components this extra copy
        helps us in that.

        Note on allow_to_build
          This is useful variable. The actual copy will have this false and
          hence will make the original copy unusable across UI. But the code
          will make a copy and save it inside widgets as child in that case
          we set allow_to_build.
          In short only instances made using copy() can setup[ and build

        Remember never do this in init only do it while build
        """
        _dict = {
            f.name: getattr(self, f.name)
            for f in dataclasses.fields(self)
        }
        # noinspection PyArgumentList
        _ret = self.__class__(**_dict)  # type: Widget
        return _ret

    def delete(self, children_only: bool = False):
        dpg.delete_item(item=self.id, children_only=children_only)

    def build_pre_runner(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):

        # ---------------------------------------------------- 01
        # check if already built
        if self.internal.is_build_done:
            e.code.CodingError(
                msgs=[
                    f"Widget is already registered with:",
                    {
                        'parent': self.internal.parent.id,
                        'with name': self.internal.name
                    },
                    f"While you are requesting to register with:",
                    {
                        'parent': parent.id,
                        'with name': name,
                    }
                ]
            )

        # ---------------------------------------------------- 02
        # check if already a child i.e. is the name taken
        if parent is not None:
            if name in parent.children.keys():
                e.code.NotAllowed(
                    msgs=[
                        f"There is already a child with name `{name}` "
                        f"in parent `{parent.id}`"
                    ]
                )
            # else we can add it as child to parent
            else:
                parent.children[name] = self

        # ---------------------------------------------------- 03
        # setup self i.e. by updating internal
        self.internal.is_build_done = True
        self.internal.name = name
        if parent is not None:
            self.internal.parent = parent
        if before is not None:
            self.internal.before = before

    @abc.abstractmethod
    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
        ...

    def build_children(self):
        """
        Here we decide how to build all children of this Widget which are
        class fields. Note that add_child will just build newly added
        components below the last child widget

        Default behaviour is to just build all fields that are Widgets one
        after other. You can of course override this to do more cosmetic
        changes to UI

        Note that `self.children` will be empty. Calling build on children
        of this widget will add it to the parent we pass. So we cannot loop
        over `self.children` instead we call build by scanning fields of
        this class. This also helps when we override this method where we
        need not add widget to `parent.children`
        """
        for f in dataclasses.fields(self):
            v = getattr(self, f.name)
            if isinstance(v, Widget):
                v.build(name=f.name, parent=self, before=None)

    def build_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):
        # build children that is fields that are widgets
        self.build_children()

        # if container close it
        if self.is_container:
            dpg.end()

        # set flag to indicate build is done
        self.internal.is_build_done = True

    def add_child(self, name: str, widget: "Widget", before: "Widget" = None):
        # make sure that you are not adding Dashboard
        if isinstance(widget, Dashboard):
            e.code.CodingError(
                msgs=[
                    f"Note that you are not allowed to add Dashboard as child "
                    f"to any Widget"
                ]
            )

        # you can add child to parent i.e. self only when it is built
        if not self.internal.is_build_done:
            e.code.NotAllowed(
                msgs=[
                    f"You cannot add chile to parent i.e. not built",
                    f"Make sure you have build the parent"
                ]
            )

        # now lets build the widget
        widget.build(name=name, parent=self, before=before)

    def preview(self):
        """
        You can see the preview of this widget without adding it to dashboard
        """
        _dash = Dashboard(
            dash_id="preview",
            title=f"PREVIEW: {self.__module__}:{self.__class__.__name__}",
        )
        _dash.build()
        _dash.add_child(
            name="child", widget=self,
        )
        _dash.run()


@dataclasses.dataclass(frozen=True)
class Dashboard(Widget):
    """
    Dashboard is nothing but specialized Window. While note that
    `widget.Window` will be any window that will be inside the Dashboard.

    Refer:
    >>> dpg.add_window

    Here we will take care of things like
    + screen resolution
    + theme
    + closing even handlers
    + favicon
    + login mechanism

    Note that we make this as primary window when we start GUI
    """
    dash_id: str
    title: str

    @property
    def id(self) -> str:
        return self.dash_id

    # noinspection PyTypeChecker,PyPropertyDefinition
    @property
    def parent(self) -> "Widget":
        e.code.CodingError(
            msgs=[
                f"You need not use this property for dash baord"
            ]
        )

    @property
    def is_container(self) -> bool:
        return True

    @property
    def dashboard(self) -> "Dashboard":
        return self

    @property
    def windows(self) -> t.Dict[str, "Window"]:
        """
        Note that windows are only added to Dashboard Widget so this property
        is only available in Dashboard

        Note do not cache this as children can dynamically alter so not
        caching will keep this property sync with any window add to children
        property
        """
        from . import Window
        return {
            k: v
            for k, v in self.children.items() if isinstance(v, Window)
        }

    # noinspection PyTypeChecker
    def copy(self) -> "Dashboard":
        e.code.CodingError(
            msgs=[
                f"this is dashboard and you need not use this method as "
                f"already this instance is eligible to be setup ..."
            ]
        )

    # noinspection PyMethodOverriding
    def build_pre_runner(self):
        # call super
        # noinspection PyTypeChecker
        super().build_pre_runner(name=self.dash_id, parent=None, before=None)

    # noinspection PyMethodMayBeStatic,PyMethodOverriding
    def build(self):

        # -------------------------------------------------- 01
        # add window
        dpg.add_window(
            name=self.id,
            label=self.title,
            on_close=self.on_close,
        )

        # -------------------------------------------------- 02
        # set the things for primary window
        # dpgc.set_main_window_size(550, 550)
        # dpgc.set_main_window_resizable(False)
        dpg.set_main_window_title(self.title)

    def run(self):

        # check if ui was built
        if not self.internal.is_build_done:
            e.code.NotAllowed(
                msgs=[
                    f"looks like you missed to build dashboard `{self.dash_id}`"
                ]
            )

        # dpgc.start_dearpygui()
        dpg.set_theme(theme="Dark Grey")
        dpg.start_dearpygui(primary_window=self.id)

    def on_close(self, sender, data):
        self.delete()
