import typing as t

from . import Widget, Dashboard
from . import widget
from . import callback
from .. import marshalling as m


def simple_split_window(
    dash_guid: str,
    title: str
) -> t.Tuple[Dashboard, widget.Group, widget.Group]:
    _dash = Dashboard(dash_guid=dash_guid, title=title)

    # noinspection PyArgumentList
    _table = widget.Table(
        header_row=False,
        resizable=True, policy=widget.TableSizingPolicy.StretchSame,
        borders_innerH=False, borders_outerH=True,
        borders_innerV=True, borders_outerV=True,
        rows=1, columns=2,
    )
    _button_cell = _table.get_cell(row=0, column=0)
    _display_cell = _table.get_cell(row=0, column=1)

    _dash.add_child(
        guid="t", widget=_table
    )

    return _dash, _button_cell, _display_cell


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
    _main_ui = widget.CollapsingHeader(
        label=title, default_open=True,
    )

    # ----------------------------------------------------- 02
    # make title and add it main ui
    _main_ui.add_child(
        guid="bb_sub_title",
        widget=widget.Text(
            f"{hashable.group_by}: {hashable.hex_hash}",
            bullet=True,
        )
    )

    # ----------------------------------------------------- 03
    # make buttons and add make them plot to _button_receiver
    _button_receiver = widget.Group()
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
    add_widgets_in_line(guid="bb_line1", receiver=_main_ui, widgets=_buttons)
    # add separator
    # _main_ui.add_child(
    #     guid='bb_sep1', widget=widget.Separator()
    # )
    # add _button_receiver display to _main_ui
    _main_ui.add_child(
        guid="bb_r", widget=_button_receiver,
    )
    # add separator
    # _main_ui.add_child(
    #     guid='bb_sep2', widget=widget.Separator()
    # )

    # ----------------------------------------------------- 04
    # return
    return _main_ui



