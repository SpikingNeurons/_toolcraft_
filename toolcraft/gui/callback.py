import dataclasses
import pathlib
from dearpygui import core as dpg
import abc
import typing as t

from .. import util
from .. import marshalling as m
from .. import storage as s
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
    callable_kwargs: t.Dict[str, t.Any] = None

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
        _callable_kwargs = \
            {} if self.callable_kwargs is None else self.callable_kwargs

        _result = getattr(
            self.hashable, self.callable_name
        )(**_callable_kwargs)

        self.receiver.add_child(
            # note that this does not take into account `self.callable_kwargs`
            guid=self.callable_name,
            widget=_result
        )
