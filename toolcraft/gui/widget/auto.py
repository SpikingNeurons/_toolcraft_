"""
********************************************************************************
** This code is auto-generated using script `scripts/dpg_widget_generator.py` **
********************        DO NOT EDIT           ******************************
********************************************************************************
"""

import dataclasses
import dearpygui.dearpygui as dpg
import typing as t
import numpy as np
import enum

from ... import marshalling as m
from .. import Widget, Callback, Color

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]


class TableSizingPolicy(m.FrozenEnum, enum.Enum):

    FixedFit = dpg.mvTable_SizingFixedFit
    FixedSame = dpg.mvTable_SizingFixedSame
    StretchProp = dpg.mvTable_SizingStretchProp
    StretchSame = dpg.mvTable_SizingStretchSame

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_TableSizingPolicy"

    @property
    def dpg_id(self) -> int:
        return self.value


class ColorMap(m.FrozenEnum, enum.Enum):

    Cool = dpg.mvPlotColormap_Cool
    Dark = dpg.mvPlotColormap_Dark
    Deep = dpg.mvPlotColormap_Deep
    Default = dpg.mvPlotColormap_Default
    Hot = dpg.mvPlotColormap_Hot
    Jet = dpg.mvPlotColormap_Jet
    Paired = dpg.mvPlotColormap_Paired
    Pastel = dpg.mvPlotColormap_Pastel
    Pink = dpg.mvPlotColormap_Pink
    Plasma = dpg.mvPlotColormap_Plasma
    Viridis = dpg.mvPlotColormap_Viridis

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_ColorMap"

    @property
    def dpg_id(self) -> int:
        return self.value


class Marker(m.FrozenEnum, enum.Enum):

    Asterisk = dpg.mvPlotMarker_Asterisk
    Circle = dpg.mvPlotMarker_Circle
    Cross = dpg.mvPlotMarker_Cross
    Diamond = dpg.mvPlotMarker_Diamond
    Down = dpg.mvPlotMarker_Down
    Left = dpg.mvPlotMarker_Left
    NONE = dpg.mvPlotMarker_None
    Plus = dpg.mvPlotMarker_Plus
    Right = dpg.mvPlotMarker_Right
    Square = dpg.mvPlotMarker_Square
    Up = dpg.mvPlotMarker_Up

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_Marker"

    @property
    def dpg_id(self) -> int:
        return self.value


class Location(m.FrozenEnum, enum.Enum):

    Center = dpg.mvPlot_Location_Center
    East = dpg.mvPlot_Location_East
    North = dpg.mvPlot_Location_North
    NorthEast = dpg.mvPlot_Location_NorthEast
    NorthWest = dpg.mvPlot_Location_NorthWest
    South = dpg.mvPlot_Location_South
    SouthEast = dpg.mvPlot_Location_SouthEast
    SouthWest = dpg.mvPlot_Location_SouthWest
    West = dpg.mvPlot_Location_West

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_Location"

    @property
    def dpg_id(self) -> int:
        return self.value


@dataclasses.dataclass(frozen=True)
class Column(Widget):
    """
    Refer:
    >>> dpg.add_table_column

    Undocumented function
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Attempt to render widget.
    show: bool = True

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    init_width_or_weight: float = 0.0

    # Default as a hidden/disabled column.
    default_hide: bool = False

    # Default as a sorting column.
    default_sort: bool = False

    # Column will stretch. Preferable with horizontal scrolling disabled
    # (default if table sizing policy is _SizingStretchSame or
    # _SizingStretchProp).
    width_stretch: bool = False

    # Column will not stretch. Preferable with horizontal scrolling enabled
    # (default if table sizing policy is _SizingFixedFit and table is
    # resizable).
    width_fixed: bool = False

    # Disable manual resizing.
    no_resize: bool = False

    # Disable manual reordering this column, this will also prevent other
    # columns from crossing over this column.
    no_reorder: bool = False

    # Disable ability to hide/disable this column.
    no_hide: bool = False

    # Disable clipping for this column (all NoClip columns will render in a
    # same draw command).
    no_clip: bool = False

    # Disable ability to sort on this field (even if
    # ImGuiTableFlags_Sortable is set on the table).
    no_sort: bool = False

    # Disable ability to sort in the ascending direction.
    no_sort_ascending: bool = False

    # Disable ability to sort in the descending direction.
    no_sort_descending: bool = False

    # Disable header text width contribution to automatic column width.
    no_header_width: bool = False

    # Make the initial sort direction Ascending when first sorting on this
    # column (default).
    prefer_sort_ascending: bool = True

    # Make the initial sort direction Descending when first sorting on this
    # column.
    prefer_sort_descending: bool = False

    # Use current Indent value when entering cell (default for column 0).
    indent_enable: bool = False

    # Ignore current Indent value when entering cell (default for columns >
    # 0). Indentation changes _within_ the cell will still be honored.
    indent_disable: bool = False

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_table_column(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            show=self.show,
            user_data=self.user_data,
            init_width_or_weight=self.init_width_or_weight,
            default_hide=self.default_hide,
            default_sort=self.default_sort,
            width_stretch=self.width_stretch,
            width_fixed=self.width_fixed,
            no_resize=self.no_resize,
            no_reorder=self.no_reorder,
            no_hide=self.no_hide,
            no_clip=self.no_clip,
            no_sort=self.no_sort,
            no_sort_ascending=self.no_sort_ascending,
            no_sort_descending=self.no_sort_descending,
            no_header_width=self.no_header_width,
            prefer_sort_ascending=self.prefer_sort_ascending,
            prefer_sort_descending=self.prefer_sort_descending,
            indent_enable=self.indent_enable,
            indent_disable=self.indent_disable,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class Row(Widget):
    """
    Refer:
    >>> dpg.table_row

    Undocumented function
    """

    # Overrides 'name' as label.
    label: str = None

    # Height of the item.
    height: int = 0

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # User data for callbacks.
    user_data: t.Any = None

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_table_row(
            **self.internal.dpg_kwargs,
            label=self.label,
            height=self.height,
            show=self.show,
            filter_key=self.filter_key,
            user_data=self.user_data,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class BTable(Widget):
    """
    Refer:
    >>> dpg.table

    Undocumented function
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # User data for callbacks.
    user_data: t.Any = None

    # show headers at the top of the columns
    header_row: bool = True

    # ...
    inner_width: int = 0

    # ...
    policy: TableSizingPolicy = None

    # ...
    freeze_rows: int = 0

    # ...
    freeze_columns: int = 0

    # Hold shift when clicking headers to sort on multiple column.
    sort_multi: bool = False

    # Allow no sorting, disable default sorting.
    sort_tristate: bool = False

    # Enable resizing columns
    resizable: bool = False

    # Enable reordering columns in header row (need calling
    # TableSetupColumn() + TableHeadersRow() to display headers)
    reorderable: bool = False

    # Enable hiding/disabling columns in context menu.
    hideable: bool = False

    # Enable sorting. Call TableGetSortSpecs() to obtain sort specs. Also
    # see ImGuiTableFlags_SortMulti and ImGuiTableFlags_SortTristate.
    sortable: bool = False

    # Right-click on columns body/contents will display table context menu.
    # By default it is available in TableHeadersRow().
    context_menu_in_body: bool = False

    # Set each RowBg color with ImGuiCol_TableRowBg or
    # ImGuiCol_TableRowBgAlt (equivalent of calling TableSetBgColor with
    # ImGuiTableBgFlags_RowBg0 on each row manually)
    row_background: bool = False

    # Draw horizontal borders between rows.
    borders_innerH: bool = False

    # Draw horizontal borders at the top and bottom.
    borders_outerH: bool = False

    # Draw vertical borders between columns.
    borders_innerV: bool = False

    # Draw vertical borders on the left and right sides.
    borders_outerV: bool = False

    # Make outer width auto-fit to columns, overriding outer_size.x value.
    # Only available when ScrollX/ScrollY are disabled and Stretch columns
    # are not used.
    no_host_extendX: bool = False

    # Make outer height stop exactly at outer_size.y (prevent auto-extending
    # table past the limit). Only available when ScrollX/ScrollY are
    # disabled. Data below the limit will be clipped and not visible.
    no_host_extendY: bool = False

    # Disable keeping column always minimally visible when ScrollX is off
    # and table gets too small. Not recommended if columns are resizable.
    no_keep_columns_visible: bool = False

    # Disable distributing remainder width to stretched columns (width
    # allocation on a 100-wide table with 3 columns
    precise_widths: bool = False

    # Disable clipping rectangle for every individual columns.
    no_clip: bool = False

    # Default if BordersOuterV is on. Enable outer-most padding. Generally
    # desirable if you have headers.
    pad_outerX: bool = False

    # Default if BordersOuterV is off. Disable outer-most padding.
    no_pad_outerX: bool = False

    # Disable inner padding between columns (double inner padding if
    # BordersOuterV is on, single inner padding if BordersOuterV is off).
    no_pad_innerX: bool = False

    # Enable horizontal scrolling. Require 'outer_size' parameter of
    # BeginTable() to specify the container size. Changes default sizing
    # policy. Because this create a child window, ScrollY is currently
    # generally recommended when using ScrollX.
    scrollX: bool = False

    # Enable vertical scrolling.
    scrollY: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_table(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            user_data=self.user_data,
            header_row=self.header_row,
            inner_width=self.inner_width,
            policy=0 if self.policy is None else self.policy.dpg_id,
            freeze_rows=self.freeze_rows,
            freeze_columns=self.freeze_columns,
            sort_multi=self.sort_multi,
            sort_tristate=self.sort_tristate,
            resizable=self.resizable,
            reorderable=self.reorderable,
            hideable=self.hideable,
            sortable=self.sortable,
            context_menu_in_body=self.context_menu_in_body,
            row_background=self.row_background,
            borders_innerH=self.borders_innerH,
            borders_outerH=self.borders_outerH,
            borders_innerV=self.borders_innerV,
            borders_outerV=self.borders_outerV,
            no_host_extendX=self.no_host_extendX,
            no_host_extendY=self.no_host_extendY,
            no_keep_columns_visible=self.no_keep_columns_visible,
            precise_widths=self.precise_widths,
            no_clip=self.no_clip,
            pad_outerX=self.pad_outerX,
            no_pad_outerX=self.no_pad_outerX,
            no_pad_innerX=self.no_pad_innerX,
            scrollX=self.scrollX,
            scrollY=self.scrollY,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()


@dataclasses.dataclass(frozen=True)
class TabButton(Widget):
    """
    Refer:
    >>> dpg.add_tab_button

    Adds a tab button to a tab bar.
    """

    # Overrides 'name' as label.
    label: str = None

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Disable reordering this tab or having another tab cross over this tab.
    no_reorder: bool = False

    # Enforce the tab position to the left of the tab bar (after the tab
    # list popup button).
    leading: bool = False

    # Enforce the tab position to the right of the tab bar (before the
    # scrolling buttons).
    trailing: bool = False

    # Disable tooltip for the given tab.
    no_tooltip: bool = False

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_tab_button(
            **self.internal.dpg_kwargs,
            label=self.label,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            no_reorder=self.no_reorder,
            leading=self.leading,
            trailing=self.trailing,
            no_tooltip=self.no_tooltip,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class TabBar(Widget):
    """
    Refer:
    >>> dpg.tab_bar

    Adds a tab bar.
    """

    # Overrides 'name' as label.
    label: str = None

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Allows for the user to change the order of the tabs.
    reorderable: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_tab_bar(
            **self.internal.dpg_kwargs,
            label=self.label,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            reorderable=self.reorderable,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class Tab(Widget):
    """
    Refer:
    >>> dpg.tab

    Adds a tab to a tab bar. Must be closed with thes end command.
    """

    # Overrides 'name' as label.
    label: str = None

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Creates a button on the tab that can hide the tab.
    closable: bool = False

    # Disable tooltip for the given tab.
    no_tooltip: bool = False

    # set using a constant
    order_mode: bool = 0

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_tab(
            **self.internal.dpg_kwargs,
            label=self.label,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            closable=self.closable,
            no_tooltip=self.no_tooltip,
            order_mode=self.order_mode,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class Button(Widget):
    """
    Refer:
    >>> dpg.add_button

    Adds a button.
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Small button, useful for embedding in text.
    small: bool = False

    # Arrow button, requires the direction keyword.
    arrow: bool = False

    # A cardinal direction for arrow.
    direction: int = 0

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_button(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            small=self.small,
            arrow=self.arrow,
            direction=self.direction,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class Combo(Widget):
    """
    Refer:
    >>> dpg.add_combo

    Adds a combo dropdown that allows a user to select a single option
    from a drop down window.
    """

    # A tuple of items to be shown in the drop down window. Can consist of
    # any combination of types.
    items: t.List[str] = ()

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Turns off functionality of widget and applies the disabled theme.
    enabled: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    default_value: str = ''

    # Align the popup toward the left.
    popup_align_left: bool = False

    # Display the preview box without the square arrow button.
    no_arrow_button: bool = False

    # Display only the square arrow button.
    no_preview: bool = False

    # mvComboHeight_Small, _Regular, _Large, _Largest
    height_mode: int = 1

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_combo(
            **self.internal.dpg_kwargs,
            items=self.items,
            label=self.label,
            width=self.width,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            enabled=self.enabled,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            default_value=self.default_value,
            popup_align_left=self.popup_align_left,
            no_arrow_button=self.no_arrow_button,
            no_preview=self.no_preview,
            height_mode=self.height_mode,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class InSameLine(Widget):
    """
    Refer:
    >>> dpg.add_same_line

    Places a widget on the same line as the previous widget. Can also be
    used for horizontal spacing.
    """

    # Overrides 'name' as label.
    label: str = None

    # Attempt to render widget.
    show: bool = True

    # User data for callbacks.
    user_data: t.Any = None

    # Offset from containing window.
    xoffset: float = 0.0

    # Offset from previous widget.
    spacing: float = -1.0

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_same_line(
            **self.internal.dpg_kwargs,
            label=self.label,
            show=self.show,
            user_data=self.user_data,
            xoffset=self.xoffset,
            spacing=self.spacing,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class Separator(Widget):
    """
    Refer:
    >>> dpg.add_separator

    Adds a horizontal line.
    """

    # Overrides 'name' as label.
    label: str = None

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # User data for callbacks.
    user_data: t.Any = None

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_separator(
            **self.internal.dpg_kwargs,
            label=self.label,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
            user_data=self.user_data,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class Child(Widget):
    """
    Refer:
    >>> dpg.child

    Adds an embedded child window. Will show scrollbars when items do not
    fit. Must be followed by a call to end.
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Shows/Hides the border around the sides.
    border: bool = True

    # Autosize the window to fit it's items in the x.
    autosize_x: bool = False

    # Autosize the window to fit it's items in the y.
    autosize_y: bool = False

    # Disable scrollbars (window can still scroll with mouse or
    # programmatically).
    no_scrollbar: bool = False

    # Allow horizontal scrollbar to appear (off by default).
    horizontal_scrollbar: bool = False

    # Shows/Hides the menubar at the top.
    menubar: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_child(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            border=self.border,
            autosize_x=self.autosize_x,
            autosize_y=self.autosize_y,
            no_scrollbar=self.no_scrollbar,
            horizontal_scrollbar=self.horizontal_scrollbar,
            menubar=self.menubar,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class Window(Widget):
    """
    Refer:
    >>> dpg.add_window

    Creates a new window for following items to be added to.
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # User data for callbacks.
    user_data: t.Any = None

    # Minimum window size.
    min_size: t.List[int] = dataclasses.field(default_factory=list)

    # Maximum window size.
    max_size: t.List[int] = dataclasses.field(default_factory=list)

    # Shows or hides the menubar.
    menubar: bool = False

    # Collapse the window.
    collapsed: bool = False

    # Autosized the window to fit it's items.
    autosize: bool = False

    # Allows for the window size to be changed or fixed.
    no_resize: bool = False

    # Title name for the title bar of the window.
    no_title_bar: bool = False

    # Allows for the window's position to be changed or fixed.
    no_move: bool = False

    # Disable scrollbars. (window can still scroll with mouse or
    # programmatically)
    no_scrollbar: bool = False

    # Disable user collapsing window by double-clicking on it.
    no_collapse: bool = False

    # Allow horizontal scrollbar to appear. (off by default)
    horizontal_scrollbar: bool = False

    # Disable taking focus when transitioning from hidden to visible state.
    no_focus_on_appearing: bool = False

    # Disable bringing window to front when taking focus. (e.g. clicking on
    # it or programmatically giving it focus)
    no_bring_to_front_on_focus: bool = False

    # Disable user closing the window by removing the close button.
    no_close: bool = False

    # Sets Background and border alpha to transparent.
    no_background: bool = False

    # Fills area behind window according to the theme and disables user
    # ability to interact with anything except the window.
    modal: bool = False

    # Fills area behind window according to the theme, removes title bar,
    # collapse and close. Window can be closed by selecting area in the
    # background behind the window.
    popup: bool = False

    # Callback ran when window is closed.
    on_close: Callback = None

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_window(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            show=self.show,
            pos=self.pos,
            delay_search=self.delay_search,
            user_data=self.user_data,
            min_size=self.min_size,
            max_size=self.max_size,
            menubar=self.menubar,
            collapsed=self.collapsed,
            autosize=self.autosize,
            no_resize=self.no_resize,
            no_title_bar=self.no_title_bar,
            no_move=self.no_move,
            no_scrollbar=self.no_scrollbar,
            no_collapse=self.no_collapse,
            horizontal_scrollbar=self.horizontal_scrollbar,
            no_focus_on_appearing=self.no_focus_on_appearing,
            no_bring_to_front_on_focus=self.no_bring_to_front_on_focus,
            no_close=self.no_close,
            no_background=self.no_background,
            modal=self.modal,
            popup=self.popup,
            on_close=self.on_close_fn,
        )
        
        return _ret

    def on_close_fn(self, **kwargs):
        if self.on_close is None:
            return None
        else:
            return self.on_close.fn()


@dataclasses.dataclass(frozen=True)
class Text(Widget):
    """
    Refer:
    >>> dpg.add_text

    Adds text. Text can have an optional label that will display to the
    right of the text.
    """

    # ...
    default_value: str = ''

    # Overrides 'name' as label.
    label: str = None

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Number of pixels until wrapping starts.
    wrap: int = -1

    # Makes the text bulleted.
    bullet: bool = False

    # Color of the text (rgba).
    color: Color = Color.DEFAULT

    # Displays the label.
    show_label: bool = False

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_text(
            **self.internal.dpg_kwargs,
            default_value=self.default_value,
            label=self.label,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            wrap=self.wrap,
            bullet=self.bullet,
            color=self.color.dpg_value,
            show_label=self.show_label,
        )
        
        return _ret


@dataclasses.dataclass(frozen=True)
class CollapsingHeader(Widget):
    """
    Refer:
    >>> dpg.collapsing_header

    Adds a collapsing header to add items to. Must be closed with the end
    command.
    """

    # Overrides 'name' as label.
    label: str = None

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Adds the ability to hide this widget by pressing the (x) in the top
    # right of widget.
    closable: bool = False

    # Sets the collapseable header open by default.
    default_open: bool = False

    # Need double-click to open node.
    open_on_double_click: bool = False

    # Only open when clicking on the arrow part.
    open_on_arrow: bool = False

    # No collapsing, no arrow (use as a convenience for leaf nodes).
    leaf: bool = False

    # Display a bullet instead of arrow.
    bullet: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_collapsing_header(
            **self.internal.dpg_kwargs,
            label=self.label,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            closable=self.closable,
            default_open=self.default_open,
            open_on_double_click=self.open_on_double_click,
            open_on_arrow=self.open_on_arrow,
            leaf=self.leaf,
            bullet=self.bullet,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class Group(Widget):
    """
    Refer:
    >>> dpg.group

    Creates a group that other widgets can belong to. The group allows
    item commands to be issued for all of its members. Must be closed with
    the end command.
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # Forces child widgets to be added in a horizontal layout.
    horizontal: bool = False

    # Spacing for the horizontal layout.
    horizontal_spacing: float = -1

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_group(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            indent=self.indent,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            horizontal=self.horizontal,
            horizontal_spacing=self.horizontal_spacing,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class Legend(Widget):
    """
    Refer:
    >>> dpg.add_plot_legend

    Adds a plot legend to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # User data for callbacks.
    user_data: t.Any = None

    # location, mvPlot_Location_*
    location: int = 5

    # ...
    horizontal: bool = False

    # ...
    outside: bool = False

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_plot_legend(
            **self.internal.dpg_kwargs,
            label=self.label,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            user_data=self.user_data,
            location=self.location,
            horizontal=self.horizontal,
            outside=self.outside,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class XAxis(Widget):
    """
    Refer:
    >>> dpg.add_plot_axis

    Adds a plot legend to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    no_gridlines: bool = False

    # ...
    no_tick_marks: bool = False

    # ...
    no_tick_labels: bool = False

    # ...
    log_scale: bool = False

    # ...
    invert: bool = False

    # ...
    lock_min: bool = False

    # ...
    lock_max: bool = False

    # ...
    time: bool = False

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_plot_axis(
            axis=dpg.mvXAxis,
            **self.internal.dpg_kwargs,
            label=self.label,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            user_data=self.user_data,
            no_gridlines=self.no_gridlines,
            no_tick_marks=self.no_tick_marks,
            no_tick_labels=self.no_tick_labels,
            log_scale=self.log_scale,
            invert=self.invert,
            lock_min=self.lock_min,
            lock_max=self.lock_max,
            time=self.time,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class YAxis(Widget):
    """
    Refer:
    >>> dpg.add_plot_axis

    Adds a plot legend to a plot.
    """

    # Overrides 'name' as label.
    label: str = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    no_gridlines: bool = False

    # ...
    no_tick_marks: bool = False

    # ...
    no_tick_labels: bool = False

    # ...
    log_scale: bool = False

    # ...
    invert: bool = False

    # ...
    lock_min: bool = False

    # ...
    lock_max: bool = False

    # ...
    time: bool = False

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_plot_axis(
            axis=dpg.mvYAxis,
            **self.internal.dpg_kwargs,
            label=self.label,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            user_data=self.user_data,
            no_gridlines=self.no_gridlines,
            no_tick_marks=self.no_tick_marks,
            no_tick_labels=self.no_tick_labels,
            log_scale=self.log_scale,
            invert=self.invert,
            lock_min=self.lock_min,
            lock_max=self.lock_max,
            time=self.time,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class SubPlot(Widget):
    """
    Refer:
    >>> dpg.subplots

    Adds a plot which is used to hold series, and can be drawn to with
    draw commands.
    """

    # ...
    rows: int

    # ...
    columns: int

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Registers a callback.
    callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    row_ratios: t.List[float] = dataclasses.field(default_factory=list)

    # ...
    column_ratios: t.List[float] = dataclasses.field(default_factory=list)

    # ...
    no_title: bool = False

    # the user will not be able to open context menus with right-click
    no_menus: bool = False

    # resize splitters between subplot cells will be not be provided
    no_resize: bool = False

    # subplot edges will not be aligned vertically or horizontally
    no_align: bool = False

    # link the y-axis limits of all plots in each row (does not apply
    # auxiliary y-axes)
    link_rows: bool = False

    # link the x-axis limits of all plots in each column
    link_columns: bool = False

    # link the x-axis limits in every plot in the subplot
    link_all_x: bool = False

    # link the y-axis limits in every plot in the subplot (does not apply to
    # auxiliary y-axes)
    link_all_y: bool = False

    # subplots are added in column major order instead of the default row
    # major order
    column_major: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_subplots(
            **self.internal.dpg_kwargs,
            rows=self.rows,
            columns=self.columns,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            callback=self.callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            row_ratios=self.row_ratios,
            column_ratios=self.column_ratios,
            no_title=self.no_title,
            no_menus=self.no_menus,
            no_resize=self.no_resize,
            no_align=self.no_align,
            link_rows=self.link_rows,
            link_columns=self.link_columns,
            link_all_x=self.link_all_x,
            link_all_y=self.link_all_y,
            column_major=self.column_major,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()


@dataclasses.dataclass(frozen=True)
class SimplePlot(Widget):
    """
    Refer:
    >>> dpg.add_simple_plot

    A simple plot for visualization of a 1 dimensional set of values.
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Overrides 'id' as value storage key.
    source: t.Optional[Widget] = None

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Used by filter widget.
    filter_key: str = ''

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    default_value: t.List[float] = ()

    # overlays text (similar to a plot title)
    overlay: str = ''

    # ...
    histogram: bool = False

    # ...
    autosize: bool = True

    # ...
    min_scale: float = 0.0

    # ...
    max_scale: float = 0.0

    @property
    def is_container(self) -> bool:
        return False

    def build(self) -> int:
        _ret = dpg.add_simple_plot(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            source=0 if self.source is None else self.source.dpg_id,
            payload_type=self.payload_type,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            filter_key=self.filter_key,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            default_value=self.default_value,
            overlay=self.overlay,
            histogram=self.histogram,
            autosize=self.autosize,
            min_scale=self.min_scale,
            max_scale=self.max_scale,
        )
        
        return _ret

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()


@dataclasses.dataclass(frozen=True)
class BPlot(Widget):
    """
    Refer:
    >>> dpg.plot

    Adds a plot which is used to hold series, and can be drawn to with
    draw commands.
    """

    # Overrides 'name' as label.
    label: str = None

    # Width of the item.
    width: int = 0

    # Height of the item.
    height: int = 0

    # Offsets the widget to the right the specified number multiplied by the
    # indent style.
    indent: int = -1

    # Sender string type must be the same as the target for the target to
    # run the payload_callback.
    payload_type: str = '$$DPG_PAYLOAD'

    # Registers a callback.
    callback: Callback = None

    # Registers a drag callback for drag and drop.
    drag_callback: Callback = None

    # Registers a drop callback for drag and drop.
    drop_callback: Callback = None

    # Attempt to render widget.
    show: bool = True

    # Places the item relative to window coordinates, [0,0] is top left.
    pos: t.List[int] = dataclasses.field(default_factory=list)

    # Used by filter widget.
    filter_key: str = ''

    # Delays searching container for specified items until the end of the
    # app. Possible optimization when a container has many children that are
    # not accessed often.
    delay_search: str = False

    # Scroll tracking
    tracked: bool = False

    # 0.0f
    track_offset: float = 0.5

    # User data for callbacks.
    user_data: t.Any = None

    # ...
    no_title: bool = False

    # ...
    no_menus: bool = False

    # ...
    no_box_select: bool = False

    # ...
    no_mouse_pos: bool = False

    # ...
    no_highlight: bool = False

    # ...
    no_child: bool = False

    # ...
    query: bool = False

    # ...
    crosshairs: bool = False

    # ...
    anti_aliased: bool = False

    # ...
    equal_aspects: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self) -> int:
        _ret = dpg.add_plot(
            **self.internal.dpg_kwargs,
            label=self.label,
            width=self.width,
            height=self.height,
            indent=self.indent,
            payload_type=self.payload_type,
            callback=self.callback_fn,
            drag_callback=self.drag_callback_fn,
            drop_callback=self.drop_callback_fn,
            show=self.show,
            pos=self.pos,
            filter_key=self.filter_key,
            delay_search=self.delay_search,
            tracked=self.tracked,
            track_offset=self.track_offset,
            user_data=self.user_data,
            no_title=self.no_title,
            no_menus=self.no_menus,
            no_box_select=self.no_box_select,
            no_mouse_pos=self.no_mouse_pos,
            no_highlight=self.no_highlight,
            no_child=self.no_child,
            query=self.query,
            crosshairs=self.crosshairs,
            anti_aliased=self.anti_aliased,
            equal_aspects=self.equal_aspects,
        )
        
        return _ret

    def callback_fn(self, **kwargs):
        if self.callback is None:
            return None
        else:
            return self.callback.fn()

    def drag_callback_fn(self, **kwargs):
        if self.drag_callback is None:
            return None
        else:
            return self.drag_callback.fn()

    def drop_callback_fn(self, **kwargs):
        if self.drop_callback is None:
            return None
        else:
            return self.drop_callback.fn()
