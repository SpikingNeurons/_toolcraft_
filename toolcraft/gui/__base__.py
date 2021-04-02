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
    allow_to_setup: bool = False
    is_setup_done: bool = False
    is_build_done: bool = False

    @property
    def id(self) -> str:
        return f"{self.parent.id}.{self.name}"

    def vars_that_can_be_overwritten(self) -> t.List[str]:
        return super().vars_that_can_be_overwritten() + \
               ['allow_to_setup', 'is_setup_done', 'is_build_done', ]


@dataclasses.dataclass(frozen=True)
class Widget(m.HashableClass, abc.ABC):

    @property
    def id(self) -> str:
        return self.internal.id

    @property
    def parent_id(self) -> str:
        return self.internal.parent.id

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
    @util.CacheResult
    def children(self) -> t.Dict[str, "Widget"]:
        # this will be populated when add_child is called
        return {}

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

        Note on allow_to_setup
          This is useful variable. The actual copy will have this false and
          hence will make the original copy unusable across UI. But the code
          will make a copy and save it inside widgets as child in that case
          we set allow_to_setup.
          In short only instances made using copy() can setup[ and build
        """
        _dict = {
            f.name: getattr(self, f.name)
            for f in dataclasses.fields(self)
        }
        # noinspection PyArgumentList
        _ret = self.__class__(**_dict)  # type: Widget
        _ret.internal.allow_to_setup = True
        return _ret

    def delete(self, children_only: bool = False):
        dpg.delete_item(item=self.id, children_only=children_only)

    def setup(self, name: str, parent: "Widget"):
        # ---------------------------------------------------- 01
        # if self is Dashboard we expect parent to be None
        if isinstance(self, Dashboard):
            if parent is not None:
                e.code.CodingError(
                    msgs=[
                        f"While setting up dashboard please supply "
                        f"parent to be None as it has no parent"
                    ]
                )
        else:
            if parent is None:
                e.code.CodingError(
                    msgs=[
                        f"Please supply parent ..."
                    ]
                )

        # ---------------------------------------------------- 02
        # check if instance is made via copy() method i.e. if it is allowed
        # to setup
        if not self.internal.allow_to_setup:
            e.code.CodingError(
                msgs=[
                    f"You need to use a widget instance obtained via copy()",
                    f"Check documentation for {Widget.copy}",
                    {
                        'parent id': parent.id, 'child name': name,
                    }
                ]
            )

        # ---------------------------------------------------- 03
        # check if already setup is done
        if self.internal.is_setup_done:
            e.code.CodingError(
                msgs=[
                    f"Widget `{self.internal.name}` is already setup with "
                    f"parent `{self.internal.parent.id}`",
                    f"So we cannot set it up with parent `{parent.id}`"
                ]
            )

        # ---------------------------------------------------- 04
        # check if already a static child
        if parent is not None:
            if name in parent.children.keys():
                e.code.NotAllowed(
                    msgs=[
                        f"There is already a child with name {name} in parent "
                        f"{parent.id}"
                    ]
                )
            # else we can add it as child to parent
            else:
                parent.children[name] = self

        # ---------------------------------------------------- 05
        # setup self i.e. by updating internal
        self.internal.is_setup_done = True
        self.internal.name = name
        if parent is not None:
            self.internal.parent = parent

        # ---------------------------------------------------- 06
        # if there are any fields that are widget please set them up as well
        # note that for add_child where we add widgets dynamically this is
        # taken care in add_child anyways
        for f in dataclasses.fields(self):
            v = getattr(self, f.name)  # type: Widget
            if isinstance(v, Widget):
                # if Dashboard raise error
                # -------------------------------------------- 06.01
                if isinstance(v, Dashboard):
                    e.code.CodingError(
                        msgs=[
                            f"Field {f.name} holds a instance for Dashboard. "
                            f"Note the we do not allow field with Dashboard "
                            f"instance ..."
                        ]
                    )

                # -------------------------------------------- 06.02
                # read documentation for copy()
                # here we will first check if the instance is not allowed to
                # setup as it is the one which is used while creating
                if v.internal.allow_to_setup:
                    e.code.CodingError(
                        msgs=[
                            f"We expect the child Widget which is not obtained "
                            f"via copy ...",
                            {
                                'parent id': self.id, 'child name': f.name
                            }
                        ]
                    )

                # -------------------------------------------- 06.03
                # hack internal __dict__ and replace it with copy ... we need
                # to do this as frozen dataclass is not supposed to be
                # updated but because of special requirement we still do it
                v = v.copy()
                self.__dict__[f.name] = v

                # -------------------------------------------- 06.04
                # setup
                v.setup(name=f.name, parent=self)

    def build_pre_runner(self, before: str = ""):
        if self.internal.is_build_done:
            e.code.CodingError(
                msgs=[
                    f"This widget `{self.id}` is already built.",
                    f"You cannot build it again"
                ]
            )

    @abc.abstractmethod
    def build(self, before: str = ""):
        ...

    def build_children(self):
        """
        Here we decide how to build all children of this Widget which are
        class fields. Note that add_child will just build newly added
        components below the last child widget

        Default behaviour is to just build all fields that are Widgets one
        after other. You can of course override this to do more cosmetic
        changes to UI
        """
        for k, w in self.children.items():
            w.build()

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

    def add_child(self, name: str, widget: "Widget"):
        # make sure that you are not adding Dashboard
        if isinstance(widget, Dashboard):
            e.code.CodingError(
                msgs=[
                    f"Note that you are not allowed to add Dashboard as child "
                    f"to any Widget"
                ]
            )

        # check if widget is already being allowed to setup
        if widget.internal.allow_to_setup:
            e.code.NotAllowed(
                msgs=[
                    f"The widget you are supplying is already allowed to be "
                    f"setup or else it was obtained via `Widget.copy()` method",
                    f"Please create a fresh copy of widget to be added as a "
                    f"child ..."
                ]
            )

        # make it possible for widget to be setup
        # note that we do not want to use copy() as it will create a duplicate
        # that also means the widget cannot be passed in multiple places as
        # we do not perform auto copy.
        widget.internal.allow_to_setup = True

        # first setup the widget
        widget.setup(name=name, parent=self)

        # now lets build the widget only if parent is built
        if self.internal.is_build_done:
            widget.build()

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
    def parent_id(self) -> str:
        e.code.CodingError(
            msgs=[
                f"You need not use this property for dash baord"
            ]
        )

    @property
    def is_container(self) -> bool:
        return True

    def init(self):
        # call super
        super().init()

        # dashboards are always allowed to be setup and there is no need to
        # make them via copy
        self.internal.allow_to_setup = True

        # setup
        # the Dashboard will never be added via `add_child` method so we need
        # to setup here in `init()`
        # noinspection PyTypeChecker
        self.setup(name=self.dash_id, parent=None)

    # noinspection PyTypeChecker
    def copy(self) -> "Dashboard":
        e.code.CodingError(
            msgs=[
                f"this is dashboard and you need not use this method as "
                f"already this instance is eligible to be setup ..."
            ]
        )

    # noinspection PyMethodMayBeStatic
    def build(self, before: str = ""):

        # -------------------------------------------------- 01
        if before != "":
            e.code.NotAllowed(
                msgs=[
                    f"Widget {self.__class__} does not support before kwarg ..."
                ]
            )

        # -------------------------------------------------- 02
        # add window
        dpg.add_window(
            name=self.id,
            label=self.title,
            on_close=self.on_close,
        )

        # -------------------------------------------------- 03
        # set the things for primary window
        # dpgc.set_main_window_size(550, 550)
        # dpgc.set_main_window_resizable(False)
        dpg.set_main_window_title(self.title)

    def run(self):
        # check if ui was built
        if not self.internal.is_setup_done:
            e.code.NotAllowed(
                msgs=[
                    f"looks like you missed to setup dashboard `{self.dash_id}`"
                ]
            )

        # check if ui was built
        if not self.internal.is_build_done:
            e.code.NotAllowed(
                msgs=[
                    f"looks like you missed to build dashboard `{self.dash_id}`"
                ]
            )

        # dpgc.start_dearpygui()
        dpg.start_dearpygui(primary_window=self.id)

    def on_close(self, sender, data):
        self.delete()
