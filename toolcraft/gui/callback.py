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
        _theme = dpg.get_value(name=self.sender.id)
        dpg.set_theme(theme=_theme)
