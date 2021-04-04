import abc
import dataclasses
import dearpygui.core as dpg
import typing as t

from ... import error as e
from ... import util
from .. import Widget, Color, Dashboard, Callback


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

    @property
    def is_container(self) -> bool:
        return False

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None
    ):

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
            callback=None if self.callback is None else self.callback.fn,
            # callback_data=self.callback_data,
        )


@dataclasses.dataclass(frozen=True)
class Combo(Widget):
    """
    Refer to
    >>> dpg.add_combo
    """

    items: t.List[str]

    default_value: str = ''

    tip: str = ''

    # Overrides 'name' as value storage key
    source: str = ''

    # Display grayed out text so selectable cannot be selected
    enabled: bool = True

    width: int = 0

    # Overrides 'name' as label
    label: str = ''

    show: bool = True

    # Align the popup toward the left by default
    popup_align_left: bool = False

    # Max ~4 items visible
    height_small: bool = False

    # Max ~8 items visible (default)
    height_regular: bool = False

    # Max ~20 items visible
    height_large: bool = False

    # As many items visible as possible
    height_largest: bool = False

    # Display on the preview box without the square arrow button
    no_arrow_button: bool = False

    # Display only a square arrow button
    no_preview: bool = False

    callback: Callback = None

    @property
    def is_container(self) -> bool:
        return False

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None
    ):
        # add_combo
        dpg.add_combo(
            **self.internal.dpg_kwargs,
            items=self.items,
            default_value=self.default_value,
            callback=None if self.callback is None else self.callback.fn,
            # callback_data=self.callback_data,
            tip=self.tip,
            source=self.source,
            enabled=self.enabled,
            width=self.width,
            label=self.label,
            show=self.show,
            popup_align_left=self.popup_align_left,
            height_small=self.height_small,
            height_regular=self.height_regular,
            height_large=self.height_large,
            height_largest=self.height_largest,
            no_arrow_button=self.no_arrow_button,
            no_preview=self.no_preview,
        )


@dataclasses.dataclass(frozen=True)
class ChildWindow(Widget):
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

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
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

    def build_pre_runner(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):

        if before is not None:
            e.code.NotAllowed(
                msgs=[
                    f"Widget {self.__class__} does not support before kwarg ..."
                ]
            )

        if not isinstance(parent, Dashboard):
            e.code.NotAllowed(
                msgs=[
                    F"Window widget can be a child only to a Dashboard",
                    f"This is because add_widow does not have parent kwarg"
                ]
            )

        super().build_pre_runner(name=name, parent=parent, before=before)

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):

        dpg.add_window(
            name=self.id,
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

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
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

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
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

    def build(
        self,
        name: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
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
                    item=self.id, column=i, width=self.widths[i]
                )


