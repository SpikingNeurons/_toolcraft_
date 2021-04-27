import dataclasses
import pathlib
from dearpygui import core as dpg
import abc
import typing as t

from .. import util
from .. import marshalling as m
from .. import storage as s
from .. import gui
from .. import error as e
from . import Widget, Callback, widget


@dataclasses.dataclass(frozen=True)
class SetThemeCallback(Callback):

    @staticmethod
    def themes() -> t.List[str]:
        return [
            "Dark", "Light", "Classic", "Dark 2", "Grey",
            "Dark Grey", "Cherry", "Purple", "Gold", "Red"
        ]

    @staticmethod
    def default_theme() -> str:
        return "Dark Grey"

    @classmethod
    def get_combo_widget(cls) -> widget.Combo:
        dpg.set_theme(theme=cls.default_theme())
        return widget.Combo(
            items=cls.themes(),
            default_value=cls.default_theme(),
            callback=cls()
        )

    def fn(self):
        _theme = dpg.get_value(name=self.sender.name)
        dpg.set_theme(theme=_theme)


@dataclasses.dataclass(frozen=True)
class CloseWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete its Parent
    """

    @classmethod
    def get_button_widget(cls) -> widget.Button:
        return widget.Button(
            label="Close [X]",
            callback=cls()
        )

    def fn(self):
        self.sender.parent.delete()


@dataclasses.dataclass(frozen=True)
class RefreshWidgetCallback(Callback):
    """
    This callback will be added to a Button that will delete its Parent and
    then call the refresh function that must ideally add the deleted widget back
    """

    refresh_callback: Callback

    @classmethod
    def get_button_widget(
        cls, refresh_callback: Callback
    ) -> widget.Button:
        return widget.Button(
            label="Refresh [R]",
            callback=cls(refresh_callback=refresh_callback)
        )

    def fn(self):
        self.sender.parent.delete()
        self.refresh_callback.fn()


@dataclasses.dataclass(frozen=True)
class HashableMethodRunnerCallback(Callback):
    """
    This callback can call a method of HashableClass.

    The method is expected to return a Widget which then will be added to
    receiver Widget as a child

    Note that method triggers only when button is clicked.

    todo: support auto refresh
    """
    title: str
    hashable: m.HashableClass
    callable_name: str
    receiver: Widget
    add_refresh_support: bool
    add_close_support: bool

    def init_validate(self):
        # call super
        super().init_validate()

        # check if receiver can accept child
        if not self.receiver.is_container:
            e.validation.NotAllowed(
                msgs=[
                    f"We expect a receiver that can accept children..."
                ]
            )

    def fn(self):
        # ----------------------------------------------------- 01
        # get some vars
        _h = self.hashable
        _unique_guid = f"{self.hashable.hex_hash}_{self.callable_name}"
        _sender = self.sender

        # ----------------------------------------------------- 02
        # dont do anything is already added to receiver
        if _unique_guid in self.receiver.children.keys():
            return

        # ----------------------------------------------------- 03
        # build the UI
        # ----------------------------------------------------- 03.01
        # everything will be added to child widget which is window with
        # scrollbar
        # todo: instead of child we can also use Window which can pop out
        _main_ui = gui.Child(
            # todo: need to support this
            menubar=False,
            border=False,
        )
        # add main ui to receiver
        self.receiver.add_child(
            guid=_unique_guid, widget=_main_ui,
        )
        # ----------------------------------------------------- 03.02
        # make title and add it main ui
        _text_title = gui.Text(msgs=self.title)
        _text_sub_title = gui.Text(
            msgs=[
                f"group by: {self.hashable.group_by_name}",
                f"callable: [{self.hashable.hex_hash}] {self.callable_name}"
            ],
            bullet=True,
        )
        _main_ui.add_child(guid="title", widget=_text_title)
        _main_ui.add_child(guid="sub_title", widget=_text_sub_title)
        # ----------------------------------------------------- 03.03
        # add buttons ... note that they remain in same line
        _buttons = []  # type: t.List[gui.Button]
        # ----------------------------------------------------- 03.03.01
        # add close button
        if self.add_close_support:
            _buttons.append(
                gui.callback.CloseWidgetCallback.get_button_widget()
            )
        # ----------------------------------------------------- 03.03.02
        # add refresh button
        if self.add_refresh_support:
            # noinspection PyUnresolvedReferences
            _buttons.append(
                gui.callback.RefreshWidgetCallback.get_button_widget(
                    self.sender.callback
                )
            )
        # ----------------------------------------------------- 03.03.03
        # keep in line
        gui.helper.keep_in_line(guid="line1", parent=_main_ui, widgets=_buttons)

        # ----------------------------------------------------- 03.04
        # add separator
        _main_ui.add_child(
            guid='separator1', widget=gui.Separator()
        )

        # ----------------------------------------------------- 03.05
        # get actual plot we are interested to display
        _result_widget = getattr(
            self.hashable, self.callable_name
        )()
        _main_ui.add_child(
            guid="result", widget=_result_widget
        )

        # ----------------------------------------------------- 03.05
        # add separator
        _main_ui.add_child(
            guid='separator2', widget=gui.Separator()
        )



