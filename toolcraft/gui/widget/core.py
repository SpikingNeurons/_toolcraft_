import abc
import dataclasses
import dearpygui.core as dpg
import typing as t

from ... import error as e
from ... import util
from ..__base__ import Widget, Color


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

    def build(self, before: str = ""):

        if before != "":
            e.code.NotAllowed(
                msgs=[
                    f"Widget {self.__class__} does not support before kwarg ..."
                ]
            )

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
            on_close=self.on_close,
        )

    def on_close(self, sender, data):
        ...


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

    def build(self, before: str = ""):
        _msgs = self.msgs if isinstance(self.msgs, list) else [self.msgs]
        for _msg in _msgs:
            dpg.add_text(
                name=_msg,
                wrap=self.wrap,
                color=self.color.dpg_value,
                bullet=self.bullet,
                tip=self.tip,
                before=before,
                source=self.source,
                default_value=self.default_value,
                show=self.show,
                parent=self.parent_id,
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

    def build(self, before: str = ""):
        dpg.add_collapsing_header(
            name=self.id,
            parent=self.parent_id,
            label=self.label,
            show=self.show,
            tip=self.tip,
            before=before,
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

    def build(self, before: str = ""):
        dpg.add_managed_columns(
            name=self.id,
            parent=self.parent_id,
            columns=self.columns,
            border=self.border,
            show=self.show,
            before=before,
        )


