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


class CallbackInternal(m.Internal):
    sender: "Widget"


@dataclasses.dataclass(frozen=True)
class Callback(m.HashableClass, abc.ABC):
    """
    Note that `Callback.fn` will as call back function.
    But when it comes to callback data we need not worry as the fields
    of this instance will serve as data ;)
    """

    @property
    @util.CacheResult
    def internal(self) -> "CallbackInternal":
        return CallbackInternal(owner=self)

    @property
    @util.CacheResult
    def sender(self) -> "Widget":
        """
        The owner i.e. the widget to which this callback was assigned
        """
        # noinspection PyTypeChecker
        return self.internal.sender

    def set_sender(self, sender: "Widget"):
        self.internal.sender = sender

    @abc.abstractmethod
    def fn(self):
        ...


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

    def init(self):
        # ------------------------------------------------------- 01
        # call super
        super().init()

        # ------------------------------------------------------- 02
        # loop over fields
        for f in dataclasses.fields(self):
            # --------------------------------------------------- 02.01
            # get value
            v = getattr(self, f.name)

            # --------------------------------------------------- 02.02
            # bind field if Widget or Callback
            if isinstance(v, (Widget, Callback)):
                self.duplicate_field(field=f, value=v)

    def duplicate_field(
        self,
        field: dataclasses.Field,
        value: t.Union["Widget", Callback]
    ):
        """
        To be called from init. Will be only called for fields that are
        Widget or Callback

        Purpose:
        + When defaults are provided copy them to mimic immutability
        + Each immutable field can have his own parent

        Why is this needed??
          Here we trick dataclass to treat some Hashable classes that were
          assigned as default to be treated as non mutable ... this helps us
          avoid using default_factory

        Who is using it ??
          + gui.Widget
            Needed only while building UI to reuse UI components and keep code
            readable. This will be in line with declarative syntax.
          + gui.Callback
            Although not needed we still allow this behaviour as it will be
            used by users that build GUI and they might get to used to assigning
            callbacks while defining class ... so just for convenience we allow
            this to happen

        Needed for fields that has default values
          When a instance is assigned during class definition then it is not
          longer usable with multiple instances of that classes. This applies in
          case of UI components. But not needed for fields like prepared_data as
          we actually might be interested to share that field with other
          instances.

          When such fields are bound for certain instance especially using the
          property internal we might want an immutable duplicate made for each
          instance.

        todo: Dont be tempted to use this behaviour in other cases like
          Model, HashableClass. Brainstorm if you think this needs
          to be done. AVOID GENERALIZING THIS FUNCTION.

        """

        # ------------------------------------------------------ 01
        # get default value
        _default_value = field.default

        # ------------------------------------------------------ 02
        # if value and _default_value are same that means we still have
        # not tricked dataclass and this is the first time things are
        # called so update __dict__ here
        # Note that the below code can also handle
        # _default_value == dataclasses.MISSING
        if id(_default_value) == id(value):
            # this makes a shallow i.e. one level copy
            # we assume that subsequent nested fields can make their own copies
            _dict = {}
            for f in dataclasses.fields(value):
                v = getattr(value, f.name)
                _dict[f.name] = v
            value = value.__class__(**_dict)
            # value = value.__class__(
            #     **{
            #         f.name: getattr(value, f.name)
            #         for f in dataclasses.fields(value)
            #     }
            # )
            # hack to override field value
            self.__dict__[field.name] = value

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

    def build_callback(self):
        # set teh sender i.e. which UI widget will have control to call this
        # callback
        for f in dataclasses.fields(self):
            v = getattr(self, f.name)
            if isinstance(v, Callback):
                v.set_sender(sender=self)

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
        # build callback
        self.build_callback()

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
