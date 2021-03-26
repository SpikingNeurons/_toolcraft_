import typing as t
import dearpygui.core as dpgc
import dearpygui.simple as dpgs

from .__base__ import Widget, WidgetContainer


class HBox(WidgetContainer):
    ...


class VBox(WidgetContainer):
    ...


class Text(Widget):
    """
    Refer to
    >>> dpgc.add_text
    """
    name: str


