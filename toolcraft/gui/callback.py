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
class HashableMethodRunnerCallback(Callback):
    """
    This callback can call a method of HashableClass.

    The method is expected to return a Widget which then will be added to
    receiver Widget as a child

    Note that method triggers only when button is clicked.
    """
    hashable: m.HashableClass
    callable_name: str
    receiver: Widget

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

        # get some vars
        # as the unique widget will be collapsing header
        _h = self.hashable
        _unique_guid = self.hashable.hex_hash + "_ch"
        _sender = self.sender

        # if not added add
        if _unique_guid not in self.receiver.children.keys():

            # make collapsing header
            _collapsing_header = gui.CollapsingHeader(
                label=self.hashable.group_by_name,
                closable=False,
                default_open=True,
            )

            # add child to receiver
            self.receiver.add_child(
                guid=_unique_guid,
                widget=_collapsing_header
            )

            # make close button and add it collapsing header
            _close_button = gui.callback.CloseWidgetCallback.get_button_widget()
            _collapsing_header.add_child(
                guid="close_button", widget=_close_button
            )

            # # create plot
            _plot = getattr(
                self.hashable, self.callable_name
            )()

            # add plot to collapsing header
            _collapsing_header.add_child(
                guid="plot", widget=_plot, before=_close_button
            )



