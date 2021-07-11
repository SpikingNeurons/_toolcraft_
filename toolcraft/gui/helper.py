import typing as t
import dearpygui.dearpygui as dpg
import enum

from . import widget, Widget, callback
from .. import marshalling as m
from .. import error as e

_DPG_IDS_CACHE = {}


def extract_dpg_ids(
    enum_class: t.Type[enum.Enum], dpg_prefix: str
) -> t.Dict[enum.Enum, int]:
    # if there return
    if enum_class in _DPG_IDS_CACHE.keys():
        return _DPG_IDS_CACHE[enum_class]

    # get as not there in cache
    try:
        _ret = {}
        for k in dir(dpg):
            if k.startswith(dpg_prefix):
                _k = k.replace(dpg_prefix, "")
                if _k == "None":
                    _k = "NONE"
                _ret[enum_class[_k]] = getattr(dpg, k)
    except KeyError as ke:
        e.code.CodingError(
            msgs=[
                f"The enum class {enum_class} has no type {ke}"
            ]
        )
        raise

    # if empty _ret there is no dpg_prefix
    if not bool(_ret):
        e.code.CodingError(
            msgs=[
                f"Cannot find dpg ids in module {dpg} that start with prefix "
                f"{dpg_prefix}"
            ]
        )

    # check if there is any enum defined that is not provided by dpg
    for _enum in enum_class:
        if _enum not in _ret.keys():
            e.code.CodingError(
                msgs=[
                    f"There is no dpg id `{dpg_prefix}{_enum.name}` present "
                    f"in module {dpg}",
                    f"So please delete enum type {_enum.name} defined in class "
                    f"{enum_class}"
                ]
            )

    # save in cache
    _DPG_IDS_CACHE[enum_class] = _ret

    # return
    return _ret


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
        guid="bb_title",
        widget=widget.Text(msgs=title)
    )
    _main_ui.add_child(
        guid="bb_sub_title",
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
    add_widgets_in_line(guid="bb_line1", receiver=_main_ui, widgets=_buttons)
    # add separator
    _main_ui.add_child(
        guid='bb_sep1', widget=widget.Separator()
    )
    # add _button_receiver display to _main_ui
    _main_ui.add_child(
        guid="bb_r", widget=_button_receiver,
    )
    # add separator
    _main_ui.add_child(
        guid='bb_sep2', widget=widget.Separator()
    )

    # ----------------------------------------------------- 04
    # return
    return _main_ui



