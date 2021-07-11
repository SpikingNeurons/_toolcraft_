import abc
import dataclasses
import dearpygui.dearpygui as dpg
import typing as t

from ... import error as e
from .. import Widget, Color, Dashboard, Callback


@dataclasses.dataclass(frozen=True)
class TabButton(Widget):
    """
    Refer to
    >>> dpg.add_tab_button
    """
    label: str = ''

    show: bool = True

    # Disable reordering this tab or having another tab cross over this tab
    no_reorder: bool = False

    # Enforce the tab position to the left of the tab bar
    # (after the tab list popup button)
    leading: bool = False

    # Enforce the tab position to the right of the tab bar
    # (before the scrolling buttons)
    trailing: bool = False

    # Disable tooltip for the given tab
    no_tooltip: bool = False

    tip: str = ''

    callback: Callback = None

    @property
    def is_container(self) -> bool:
        return False

    def build(self):
        # add_button
        dpg.add_tab_button(
            **self.internal.dpg_kwargs,
            label=self.label,
            show=self.show,
            no_reorder=self.no_reorder,
            leading=self.leading,
            trailing=self.trailing,
            no_tooltip=self.no_tooltip,
            tip=self.tip,
            callback=None if self.callback is None else self.callback.fn,
        )


@dataclasses.dataclass(frozen=True)
class TabBar(Widget):
    """
    Refer to
    >>> dpg.add_tab_bar
    """
    # allows for moveable tabs
    reorderable: bool = False
    show: bool = True
    callback: Callback = None

    @property
    def is_container(self) -> bool:
        return True

    def build(self):
        # add_button
        dpg.add_tab_bar(
            **self.internal.dpg_kwargs,
            reorderable=self.reorderable,
            show=self.show,
            callback=None if self.callback is None else self.callback.fn,
        )


@dataclasses.dataclass(frozen=True)
class Tab(Widget):
    """
    Refer to
    >>> dpg.add_tab
    """

    # creates a button on the tab that can hide the tab
    closable: bool = False

    label: str = ''

    show: bool = True

    # Disable reordering this tab or having another tab cross over this tab
    no_reorder: bool = False

    # Enforce the tab position to the left of the tab bar
    # (after the tab list popup button)
    leading: bool = False

    # Enforce the tab position to the right of the tab bar
    # (before the scrolling buttons)
    trailing: bool = False

    # Disable tooltip for the given tab
    no_tooltip: bool = False

    tip: str = ''

    @property
    def is_container(self) -> bool:
        return True

    def build(self):
        # add_button
        dpg.add_tab(
            **self.internal.dpg_kwargs,
            closable=self.closable,
            label=self.label,
            show=self.show,
            no_reorder=self.no_reorder,
            leading=self.leading,
            trailing=self.trailing,
            no_tooltip=self.no_tooltip,
            tip=self.tip,
        )


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
    Refer to
    >>> dpg.add_same_line
    """

    # offset from containing window
    xoffset: float = 0.0

    # offset from previous widget
    spacing: float = -1.0

    show: bool = True

    @property
    def is_container(self) -> bool:
        return False

    def build(self):
        dpg.add_same_line(
            **self.internal.dpg_kwargs,
            xoffset=self.xoffset,
            spacing=self.spacing,
            show=self.show,
        )


@dataclasses.dataclass(frozen=True)
class Columns(Widget):
    """
    Refer to
    >>> dpg.add_columns
    """
    columns: int
    border: bool = True
    show: bool = True

    @property
    def is_container(self) -> bool:
        return False

    def build(self):
        dpg.add_columns(
            **self.internal.dpg_kwargs,
            columns=self.columns,
            border=self.border,
            show=self.show,
        )


@dataclasses.dataclass(frozen=True)
class NextColumn(Widget):
    """
    Refer to
    >>> dpg.add_next_column
    """
    show: bool = True

    @property
    def is_container(self) -> bool:
        return False

    def build(self):
        dpg.add_next_column(
            **self.internal.dpg_kwargs,
            show=self.show,
        )


@dataclasses.dataclass(frozen=True)
class Separator(Widget):
    """
    Refer to
    >>> dpg.add_separator
    """
    tip: str = ''

    @property
    def is_container(self) -> bool:
        return False

    def build(self):
        dpg.add_separator(
            **self.internal.dpg_kwargs,
            tip=self.tip,
        )


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
    Refer to
    >>> dpg.add_window
    """

    width: int = -1

    height: int = -1

    # x position the window will start at
    x_pos: int = 200

    # y position the window will start at
    y_pos: int = 200

    # Autosized the window to fit it's items.
    autosize: bool = False

    # Allows for the window size to be changed or fixed
    no_resize: bool = False

    # Title name for the title bar of the window
    no_title_bar: bool = False

    # Allows for the window's position to be changed or fixed
    no_move: bool = False

    # Disable scrollbars
    # (window can still scroll with mouse or programmatically)
    no_scrollbar: bool = False

    # Disable user collapsing window by double-clicking on it
    no_collapse: bool = False

    # Allow horizontal scrollbar to appear (off by default).
    horizontal_scrollbar: bool = False

    # Disable taking focus when transitioning from hidden to visible state
    no_focus_on_appearing: bool = False

    # Disable bringing window to front when taking focus
    # (e.g. clicking on it or programmatically giving it focus)
    no_bring_to_front_on_focus: bool = False

    menubar: bool = False

    no_close: bool = False

    no_background: bool = False

    label: str = ''

    # Attempt to render
    show: bool = True

    # Collapse the window
    collapsed: bool = False

    on_close: Callback = None

    @property
    def is_container(self) -> bool:
        return True

    def build_pre_runner(self):

        if self.internal.before is not None:
            e.code.NotAllowed(
                msgs=[
                    f"Widget {self.__class__} does not support before kwarg ..."
                ]
            )

        if not isinstance(self.internal.parent, Dashboard):
            e.code.NotAllowed(
                msgs=[
                    F"Window widget can be a child only to a Dashboard",
                    f"This is because add_widow does not have parent kwarg"
                ]
            )

        super().build_pre_runner()

    def build(self):

        dpg.add_window(
            name=self.name,
            width=self.width,
            height=self.height,
            x_pos=self.x_pos,
            y_pos=self.y_pos,
            autosize=self.autosize,
            no_resize=self.no_resize,
            no_title_bar=self.no_title_bar,
            no_move=self.no_move,
            no_scrollbar=self.no_scrollbar,
            no_collapse=self.no_collapse,
            horizontal_scrollbar=self.horizontal_scrollbar,
            no_focus_on_appearing=self.no_focus_on_appearing,
            no_bring_to_front_on_focus=self.no_bring_to_front_on_focus,
            menubar=self.menubar,
            no_close=self.no_close,
            no_background=self.no_background,
            label=self.label,
            show=self.show,
            collapsed=self.collapsed,
            on_close=None if self.on_close is None else self.on_close.fn,
        )


@dataclasses.dataclass(frozen=True)
class Text(Widget):
    """
    Refer:
    >>> dpg.add_text

    Adds text. Text can have an optional label that will display to the
    right of the text.
    """
    # ...
    msgs: t.Union[str, t.List[str]]

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
        _msgs = self.msgs if isinstance(self.msgs, list) else [self.msgs]

        _ids = []

        for _msg in _msgs:
            # noinspection PyUnresolvedReferences
            _ret = dpg.add_text(
                **self.internal.dpg_kwargs,
                default_value=_msg,
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

            _ids.append(_ret)

        # currently returning the first one
        # todo: fix this
        return _ids[0]


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
class ManagedColumn(Widget):
    """
    Refer to
    >>> dpg.add_managed_columns
    """
    columns: int
    border: bool = True
    show: bool = True
    widths: t.List[float] = None

    @property
    def is_container(self) -> bool:
        return True

    def init_validate(self):
        # check if num of elements in widths is same as number of columns
        if self.widths is not None:
            if len(self.widths) != self.columns:
                e.validation.NotAllowed(
                    msgs=[
                        f"The widths field should have {self.columns} elements",
                        f"Found {len(self.widths)} elements in widths instead"
                    ]
                )

    def build(self):
        # add ui component
        dpg.add_managed_columns(
            **self.internal.dpg_kwargs,
            columns=self.columns,
            border=self.border,
            show=self.show,
        )

        # set column widths
        # todo: this feature is still not working
        #   issue filed here: https://github.com/hoffstadt/DearPyGui/issues/780
        if self.widths is not None:
            for i in range(self.columns):
                dpg.set_managed_column_width(
                    item=self.name, column=i, width=self.widths[i]
                )
