import abc
import dataclasses
import dearpygui.core as dpgc
import dearpygui.simple as dpgs
import typing as t

from ... import error as e
from ... import util
from ..__base__ import Widget, WidgetContainer, Color


@dataclasses.dataclass(frozen=True)
class Text(Widget):
    """
    Refer to
    >>> dpgc.add_text
    """
    msgs: t.Union[str, t.List[str]]

    wrap: int = -1
    color: Color = Color.WHITE
    bullet: bool = False
    tip: str = ""
    before: str = ""
    source: str = ""
    default_value: str = ""
    show: bool = True

    def make_gui(self):
        _msgs = self.msgs if isinstance(self.msgs, list) else [self.msgs]
        for _msg in _msgs:
            dpgc.add_text(
                name=_msg,
                wrap=self.wrap,
                color=self.color.dpg_value,
                bullet=self.bullet,
                tip=self.tip,
                before=self.before,
                source=self.source,
                default_value=self.default_value,
                show=self.show,
                parent=self.parent_id,
            )


@dataclasses.dataclass(frozen=True)
class CollapsingHeader(Widget, abc.ABC):
    """
    Refer to
    >>> dpgs.collapsing_header
    """
    label: str = ""
    show: bool = True
    tip: str = ""
    before: str = ""
    closable: bool = False
    default_open: bool = False
    open_on_double_click: bool = False
    open_on_arrow: bool = False
    leaf: bool = False
    bullet: bool = False

    def init_validate(self):
        # call super
        super().init_validate()

        # check if children available
        if not bool(self.children):
            e.code.CodingError(
                msgs=[
                    f"Please provide dataclass fields that are widgets",
                    f"There is nothing to render ... please check class "
                    f"{self.__class__}"
                ]
            )

    def make_gui(self):
        with dpgs.collapsing_header(
            name=self.id,
            parent=self.parent_id,
            label=self.label,
            show=self.show,
            tip=self.tip,
            before=self.before,
            closable=self.closable,
            default_open=self.default_open,
            open_on_double_click=self.open_on_double_click,
            open_on_arrow=self.open_on_arrow,
            leaf=self.leaf,
            bullet=self.bullet,
        ):
            # make call to build gui for children
            self.make_children_gui()


@dataclasses.dataclass(frozen=True)
class ManagedColumn(WidgetContainer):
    """
    Refer to
    >>> dpgs.managed_columns
    """
    columns: int
    border: bool = True
    show: bool = True
    before: str = ""

    def make_gui(self):

        with dpgs.managed_columns(
            name=self.id,
            parent=self.parent_id,
            columns=self.columns,
            border=self.border,
            show=self.show,
            before=self.before,
        ):
            # make guis for children
            self.make_children_gui()



