import typing as t
from dearpygui import core as dpg
from . import widget, Widget


def keep_in_line(
    guid: str,
    parent: Widget,
    widgets: t.List[Widget]
):
    parent.add_child(
        guid=f"{guid}_{0}",
        widget=widgets[0],
    )
    for i, w in enumerate(widgets[1:]):
        parent.add_child(
            guid=f"{guid}_{i}_il",
            widget=widget.InSameLine()
        )
        parent.add_child(
            guid=f"{guid}_{i+1}",
            widget=w,
        )

