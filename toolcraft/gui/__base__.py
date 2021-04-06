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
from . import assets

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
    def name(self) -> str:
        """
        This is basically using only senders info to build unique name
        Currently we assume there will be only one Callback per widget so we
        need not worry.

        todo: If there are multiple callbacks for widget we might need to
          update this code, where we need to accept extra unique token like
          guid and add it as mandatory field for this class
        """
        return f"[{self.yaml_tag()}]{self.sender.name}"

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

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!{cls.__name__}"

    def init_validate(self):
        # call super
        super().init_validate()

        # check for MANDATORY
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if v == MANDATORY:
                e.validation.NotAllowed(
                    msgs=[
                        f"Please supply value for mandatory field {f_name} "
                        f"of class {self.__class__}"
                    ]
                )

    def set_sender(self, sender: "Widget"):
        self.internal.sender = sender

    @abc.abstractmethod
    def fn(self):
        ...


class WidgetInternal(m.Internal):
    guid: str
    parent: t.Union["Dashboard", "Widget"]
    before: t.Optional["Widget"]
    is_build_done: bool

    @property
    def name(self) -> str:
        return f"{self.parent.name}.{self.guid}"

    @property
    def dpg_kwargs(self) -> t.Dict[str, t.Any]:
        return dict(
            name=self.name,
            parent=self.parent.name,
            before="" if self.before is None else self.before.name
        )


@dataclasses.dataclass(frozen=True)
class Widget(m.HashableClass, abc.ABC):

    @property
    def guid(self) -> str:
        return self.internal.guid

    @property
    def name(self) -> str:
        _internal = self.internal
        return f"{_internal.parent.name}.{_internal.guid}"

    @property
    def parent(self) -> "Widget":
        if isinstance(self.internal.parent, str):
            raise Exception(self.internal.parent)
        return self.internal.parent

    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        return WidgetInternal(owner=self)

    @property
    def is_built(self) -> bool:
        return self.internal.has(item="is_build_done")

    @property
    @abc.abstractmethod
    def is_container(self) -> bool:
        """
        If the dpg component needs a call to end
        Needed when the component is container and is used in with context
        To figure out which component is container refer to
        >>> from dearpygui import simple
        And check which methods decorated with `@contextmanager` are making
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
        # if not container raise error
        if not self.is_container:
            e.code.NotAllowed(
                msgs=[
                    f"This property is not available for Widgets that do not "
                    f"support containers",
                    f"Please check class {self.__class__}"
                ]
            )
        # this will be populated when add_child is called
        return {}

    def init_validate(self):
        # call super
        super().init_validate()

        # check for MANDATORY
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if v == MANDATORY:
                e.validation.NotAllowed(
                    msgs=[
                        f"Please supply value for mandatory field {f_name} "
                        f"of class {self.__class__}"
                    ]
                )

    def init(self):
        # ------------------------------------------------------- 01
        # call super
        super().init()

        # ------------------------------------------------------- 02
        # loop over fields
        for f_name in self.dataclass_field_names:
            # --------------------------------------------------- 02.01
            # get value
            v = getattr(self, f_name)

            # --------------------------------------------------- 02.02
            # bind field if Widget or Callback
            if isinstance(v, (Widget, Callback)):
                self.duplicate_field(field_name=f_name, value=v)

    def duplicate_field(
        self,
        field_name: str,
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
        # get field and its default value
        _field = self.__dataclass_fields__[field_name]
        _default_value = _field.default

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
            for f_name in value.dataclass_field_names:
                v = getattr(value, f_name)
                _dict[f_name] = v
            value = value.__class__(**_dict)
            # hack to override field value
            self.__dict__[field_name] = value

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

    def delete(self):
        # delete self from parents children
        del self.parent.children[self.guid]
        # delete the UI counterpart
        dpg.delete_item(item=self.name, children_only=False)

    def layout(self):
        """
        Here we decide how to layout all children of this Widget which are
        class fields.

        Note that any widgets that are added dynamically apart from widget
        class fields with add_child later will just build newly added
        components below the last child widget. This can be controlled via
        `parent` and `before` argument anyways/

        Default behaviour is to just build all fields that are Widgets one
        after other. You can of course override this to do more cosmetic
        changes to UI

        Note that we cannot simply loop over children dict because
        + if add_child was called before build() then there will be some
          items in dict
        + the widgets that are fields of this class are not yet added to
          children
        + before calling layout we keep a copy of items that are added in
          children dict and clear the dict. So dict will be empty here
        """
        # ----------------------------------------------------- 01
        # make sure that children dict is empty
        # this is needed because layout will decide the order of children and
        # about rendering them
        if bool(self.children):
            e.code.CodingError(
                msgs=[
                    f"Note that children dict is not empty",
                    "If you have performed add_child before build the code "
                    "before call to layout should back them up and clear "
                    "children dict"
                ]
            )

        # ----------------------------------------------------- 02
        # if there is a widget which is field of this widget then add it
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if isinstance(v, Widget):
                self.add_child(guid=f_name, widget=v, before=None)

    def build_pre_runner(self):

        # ---------------------------------------------------- 01
        # check if already built
        if self.is_built:
            e.code.CodingError(
                msgs=[
                    f"Widget is already built and registered with:",
                    {
                        'parent': self.internal.parent.name,
                        'guid': self.guid
                    },
                ]
            )

        # ---------------------------------------------------- 02
        # set the sender i.e. which UI widget will have control to call this
        # callback
        for f_name in self.dataclass_field_names:
            v = getattr(self, f_name)
            if isinstance(v, Callback):
                v.set_sender(sender=self)

        # ---------------------------------------------------- 03
        # layout ... only done for widgets that are containers
        if self.is_container:
            # ------------------------------------------------ 03.01
            # backup children dict before clearing it
            # this si needed because in some cases there will be add_child
            # performed before build, but we need to give preference to layout
            # method and then again append the backed up elements
            _backup_children = {
                k: v for k, v in self.children.items()
            }
            # ------------------------------------------------ 03.02
            # clear the children dict
            self.children.clear()
            # ------------------------------------------------ 03.03
            # call layout it will add some widgets if any
            self.layout()
            # ------------------------------------------------ 03.04
            # update children with backup
            for k, v in _backup_children.items():
                if k in self.children.keys():
                    e.code.CodingError(
                        msgs=[
                            f"The `layout()` method has added child with guid "
                            f"`{k}` which was already added before `build()` "
                            f"was called"
                        ]
                    )
                self.children[k] = v

    @abc.abstractmethod
    def build(self):
        ...

    def build_post_runner(
        self, *, hooked_method_return_value: t.Any
    ):

        # if container build children
        if self.is_container:

            # now as layout is completed and build for this widget is completed,
            # now it is time to render children
            for child in self.children.values():
                child.build()

            # also close the dpg based end as we do not use with context
            dpg.end()

        # set flag to indicate build is done
        self.internal.is_build_done = True

    def add_child(
        self,
        guid: str,
        widget: "Widget",
        before: "Widget" = None,
    ):
        # -------------------------------------------------- 01
        # validations
        # -------------------------------------------------- 01.01
        # if not container we cannot add widgets
        if not self.is_container:
            e.code.CodingError(
                msgs=[
                    f"Widget {self.__class__} is not of container type. We "
                    f"do not support adding widget as child"
                ]
            )
        # -------------------------------------------------- 01.02
        # make sure that you are not adding Dashboard
        if isinstance(widget, Dashboard):
            e.code.CodingError(
                msgs=[
                    f"Note that you are not allowed to add Dashboard as child "
                    f"to any Widget"
                ]
            )

        # -------------------------------------------------- 02
        # if widget is already built then raise error
        if widget.is_built:
            e.code.NotAllowed(
                msgs=[
                    f"The widget is already built with:",
                    {
                        'parent': widget.parent.name,
                        'guid': widget.guid
                    },
                    f"You are now attempting to build it again with",
                    {
                        'parent': self.name,
                        'guid': guid
                    }
                ]
            )

        # -------------------------------------------------- 02
        # if guid in children raise error
        if guid in self.children.keys():
            e.validation.NotAllowed(
                msgs=[
                    f"Looks like the widget with guid `{guid}` is already "
                    f"added to parent."
                ]
            )

        # -------------------------------------------------- 03
        # set internals
        widget.internal.guid = guid
        widget.internal.parent = self
        widget.internal.before = before

        # -------------------------------------------------- 04
        # we can now store widget to children
        # Note that guid is used as it is for dict key
        self.children[guid] = widget

        # -------------------------------------------------- 05
        # if this widget is already built we need to build this widget here
        # else it will be built when build() on super parent is called
        if self.is_built:
            widget.build()

    def hide(self, children_only: bool = False):
        # todo: needs testing
        if children_only:
            for child in dpg.get_item_children(item=self.id):
                dpg.configure_item(item=child, show=False)
        else:
            dpg.configure_item(item=self.id, show=False)

    def show(self, children_only: bool = False):
        # todo: needs testing
        if children_only:
            for child in dpg.get_item_children(item=self.id):
                dpg.configure_item(item=child, show=True)
        else:
            dpg.configure_item(item=self.id, show=True)

    def preview(self):
        """
        You can see the preview of this widget without adding it to dashboard
        """
        _dash = Dashboard(
            dash_guid="preview",
            title=f"PREVIEW: {self.__module__}:{self.__class__.__name__}",
        )
        _dash.build()
        _dash.add_child(guid="child", widget=self)
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
    dash_guid: str
    title: str

    @property
    def name(self) -> str:
        return self.dash_guid

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

    # noinspection PyTypeChecker,PyMethodMayBeStatic
    def copy(self) -> "Dashboard":
        e.code.CodingError(
            msgs=[
                f"this is dashboard and you need not use this method as "
                f"already this instance is eligible to be setup ..."
            ]
        )

    # noinspection PyMethodMayBeStatic,PyMethodOverriding
    def build(self):

        # -------------------------------------------------- 01
        # add window
        dpg.add_window(
            name=self.name,
            label=self.title,
            on_close=self.on_close,
        )

        # -------------------------------------------------- 02
        # set the things for primary window
        # dpgc.set_main_window_size(550, 550)
        dpg.set_theme(theme="Dark Grey")
        dpg.set_main_window_pos(x=0, y=0)
        dpg.set_main_window_size(width=1370, height=740)
        # dpgc.set_main_window_resizable(False)
        dpg.set_main_window_title(self.title)

        assets.Font.RobotoRegular.set(size=16)

        # dpg.set_style_window_border_size(0.0)
        # dpg.set_style_child_border_size(0.0)
        # dpg.set_style_window_title_align(0.5, 0.5)
        dpg.set_style_window_rounding(0.0)
        dpg.set_style_frame_rounding(0.0)

        # dpg.set_theme_item(dpg.mvGuiCol_TextDisabled, 143, 143, 143, 255)
        # dpg.set_theme_item(dpg.mvGuiCol_Separator, 127, 127, 127, 255)

    def run(self):

        # check if ui was built
        if not self.internal.is_build_done:
            e.code.NotAllowed(
                msgs=[
                    f"looks like you missed to build dashboard "
                    f"`{self.name}`"
                ]
            )

        # dpgc.start_dearpygui()
        dpg.set_theme(theme="Dark Grey")
        dpg.start_dearpygui(primary_window=self.name)

    def on_close(self, sender, data):
        self.delete()
