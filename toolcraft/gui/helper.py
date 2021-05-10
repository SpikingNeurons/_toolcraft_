import typing as t
from dearpygui import core as dpg
from . import widget, Widget, callback
from .. import marshalling as m


def add_widgets_in_line(
    guid: str,
    receiver: Widget,
    widgets: t.List[Widget]
):
    receiver.add_child(
        guid=f"{guid}_{0}",
        widget=widgets[0],
    )
    for i, w in enumerate(widgets[1:]):
        receiver.add_child(
            guid=f"{guid}_{i}_il",
            widget=widget.InSameLine()
        )
        receiver.add_child(
            guid=f"{guid}_{i+1}",
            widget=w,
        )


def button_bar_from_hashable_callables(
    tab_group_name: str,
    hashable: m.HashableClass,
    title: str,
    close_button: bool,
    callable_names: t.Dict[str, str],
) -> Widget:
    # ----------------------------------------------------- 01
    # everything will be added to main UI which is window with
    # scrollbar
    # todo: instead of child we can also use Window which can pop out
    _main_ui = widget.Child(
        # todo: need to support this
        menubar=False,
        border=False,
        # height=500,
        # autosize_y=False,
    )

    # ----------------------------------------------------- 02
    # make title and add it main ui
    _main_ui.add_child(
        guid="title",
        widget=widget.Text(msgs=title)
    )
    _main_ui.add_child(
        guid="sub_title",
        widget=widget.Text(
            msgs=[
                f"{hashable.group_by}: {hashable.hex_hash}",
            ],
            bullet=True,
        )
    )

    # ----------------------------------------------------- 03
    # make buttons and add make them plot to _button_receiver
    _button_receiver = widget.Child(
        menubar=False, border=False, height=450)
    # make button bar
    _buttons = []
    # add close button
    if close_button:
        _buttons.append(
            callback.CloseWidgetCallback.get_button_widget()
        )
    # make buttons for callable names
    for _button_label, _callable_name in callable_names.items():
        _b = hashable.get_gui_button(
            tab_group_name=tab_group_name,
            button_label=_button_label,
            callable_name=_callable_name,
            receiver=_button_receiver,
            allow_refresh=True,
        )
        _buttons.append(_b)
    # add buttons to _main_ui
    add_widgets_in_line(guid="line1", receiver=_main_ui, widgets=_buttons)
    # add separator
    _main_ui.add_child(
        guid='separator1', widget=widget.Separator()
    )
    # add _button_receiver display to _main_ui
    _main_ui.add_child(
        guid="display", widget=_button_receiver,
    )
    # add separator
    _main_ui.add_child(
        guid='separator2', widget=widget.Separator()
    )

    # ----------------------------------------------------- 04
    # return
    return _main_ui



