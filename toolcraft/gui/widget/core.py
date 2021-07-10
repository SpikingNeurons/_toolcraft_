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
    Refer to
    >>> dpg.add_button
    """

    # Small button, useful for embedding in text.
    small: bool = False

    # Arrow button, must use with direction
    arrow: bool = False

    # A cardinal direction
    direction: int = 0

    tip: str = ''

    width: int = 0

    height: int = 0

    # Overrides 'name' as label
    label: str = ''

    show: bool = True

    enabled: bool = True

    callback: Callback = None

    def init_validate(self):
        # call super
        super().init_validate()

        # if callback_fn is overridden then never supply field callback
        if Button.callback_fn != self.__class__.callback_fn:
            if self.callback is not None:
                e.code.CodingError(
                    msgs=[
                        f"Please do not supply `callback` field as you have "
                        f"overridden method `callback_fn` in class "
                        f"{self.__class__}"
                    ]
                )

    @property
    def is_container(self) -> bool:
        return False

    def build(self):

        # add_button
        dpg.add_button(
            **self.internal.dpg_kwargs,
            small=self.small,
            arrow=self.arrow,
            direction=self.direction,
            tip=self.tip,
            width=self.width,
            height=self.height,
            # note that name is taken and used by self.id which is very long
            label=self.label,
            show=self.show,
            enabled=self.enabled,
            callback=self.callback_fn,
            # callback_data=self.callback_data,
        )

    def callback_fn(self, **kwargs):
        """
        todo: we should add such function for all widgets that use callback
          This can help when you override this method by defining a subclass
          instead of supplying Callback instance for field callback
        """
        if self.callback is not None:
            self.callback.fn()


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
    Refer to
    >>> dpg.add_child
    """

    # Attempt to render
    show: bool = True

    # Adds a simple tooltip
    tip: str = ''

    width: int = 0

    height: int = 0

    border: bool = True

    # Autosize the window to fit it's items in the x.
    autosize_x: bool = True

    # Autosize the window to fit it's items in the y.
    autosize_y: bool = True

    # Disable scrollbars
    # (window can still scroll with mouse or programmatically)
    no_scrollbar: bool = False

    # Allow horizontal scrollbar to appear (off by default).
    horizontal_scrollbar: bool = False

    menubar: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self):
        dpg.add_child(
            **self.internal.dpg_kwargs,
            show=self.show,
            tip=self.tip,
            width=self.width,
            height=self.height,
            border=self.border,
            autosize_x=self.autosize_x,
            autosize_y=self.autosize_y,
            no_scrollbar=self.no_scrollbar,
            horizontal_scrollbar=self.horizontal_scrollbar,
            menubar=self.menubar,
        )


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
    Refer to
    >>> dpg.add_text
    """
    msgs: t.Union[str, t.List[str]]
    wrap: int = -1
    color: Color = Color.WHITE
    bullet: bool = False
    tip: str = ""
    source: str = ""
    default_value: str = ""
    show: bool = True

    @property
    def is_container(self) -> bool:
        return False

    def build(self):
        _dpg_kwargs = self.internal.dpg_kwargs
        _msgs = self.msgs if isinstance(self.msgs, list) else [self.msgs]
        for _msg in _msgs:
            _dpg_kwargs['name'] = _msg
            dpg.add_text(
                **_dpg_kwargs,
                wrap=self.wrap,
                color=self.color.dpg_value,
                bullet=self.bullet,
                tip=self.tip,
                source=self.source,
                default_value=self.default_value,
                show=self.show,
            )


@dataclasses.dataclass(frozen=True)
class CollapsingHeader(Widget, abc.ABC):
    """
    Refer to
    >>> dpg.add_collapsing_header
    """
    label: str = ""
    show: bool = True
    tip: str = ""
    closable: bool = False
    default_open: bool = False
    open_on_double_click: bool = False
    open_on_arrow: bool = False
    leaf: bool = False
    bullet: bool = False

    @property
    def is_container(self) -> bool:
        return True

    def build(self):
        dpg.add_collapsing_header(
            **self.internal.dpg_kwargs,
            label=self.label,
            show=self.show,
            tip=self.tip,
            closable=self.closable,
            default_open=self.default_open,
            open_on_double_click=self.open_on_double_click,
            open_on_arrow=self.open_on_arrow,
            leaf=self.leaf,
            bullet=self.bullet,
        )


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


