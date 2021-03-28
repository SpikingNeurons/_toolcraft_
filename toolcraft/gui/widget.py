import abc
import dataclasses
import dearpygui.core as dpgc
import dearpygui.simple as dpgs
import typing as t

from .. import error as e
from .. import util
from .__base__ import Widget, WidgetContainer, Color, PLOT_DATA_TYPE, \
    PlotColorMap

# noinspection PyUnreachableCode
if False:
    from .plot_types import PlotType


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
class SimplePlot(Widget):
    """
    Refer to
    >>> dpgc.add_simple_plot
    """
    value: PLOT_DATA_TYPE
    overlay: str = ""
    minscale: float = 0.0
    maxscale: float = 0.0
    histogram: bool = False
    tip: str = ""
    before: str = ""
    width: int = 0
    height: int = 0
    source: str = ""
    label: str = ""
    show: bool = True

    def make_gui(self):
        dpgc.add_simple_plot(
            name=self.id,
            parent=self.parent_id,
            value=self.value,
            overlay=self.overlay,
            minscale=self.minscale,
            maxscale=self.maxscale,
            histogram=self.histogram,
            tip=self.tip,
            before=self.before,
            width=self.width,
            height=self.height,
            source=self.source,
            label=self.label,
            show=self.show,
        )


@dataclasses.dataclass(frozen=True)
class Plot(WidgetContainer):
    """
    Refer to
    >>> dpgc.add_plot
    """

    items: t.List["PlotType"]

    # the defaults supported by dearpygui
    label: str = ''
    x_axis_name: str = ''
    y_axis_name: str = ''
    no_legend: bool = False
    no_menus: bool = False
    no_box_select: bool = False
    no_mouse_pos: bool = False
    no_highlight: bool = False
    no_child: bool = False
    query: bool = False
    crosshairs: bool = False
    anti_aliased: bool = False
    equal_aspects: bool = False
    yaxis2: bool = False
    yaxis3: bool = False
    xaxis_no_gridlines: bool = False
    xaxis_no_tick_marks: bool = False
    xaxis_no_tick_labels: bool = False
    xaxis_log_scale: bool = False
    xaxis_time: bool = False
    xaxis_invert: bool = False
    xaxis_lock_min: bool = False
    xaxis_lock_max: bool = False
    yaxis_no_gridlines: bool = False
    yaxis_no_tick_marks: bool = False
    yaxis_no_tick_labels: bool = False
    yaxis_log_scale: bool = False
    yaxis_invert: bool = False
    yaxis_lock_min: bool = False
    yaxis_lock_max: bool = False
    y2axis_no_gridlines: bool = False
    y2axis_no_tick_marks: bool = False
    y2axis_no_tick_labels: bool = False
    y2axis_log_scale: bool = False
    y2axis_invert: bool = False
    y2axis_lock_min: bool = False
    y2axis_lock_max: bool = False
    y3axis_no_gridlines: bool = False
    y3axis_no_tick_marks: bool = False
    y3axis_no_tick_labels: bool = False
    y3axis_log_scale: bool = False
    y3axis_invert: bool = False
    y3axis_lock_min: bool = False
    y3axis_lock_max: bool = False
    # Parent to add this item to. (runtime adding)
    parent: str = ''
    # This item will be displayed before the specified item in the parent.
    # (runtime adding)
    before: str = ''
    width: int = -1
    height: int = -1
    # Callback ran when plot is queried. Should be of the form
    # 'def Callback(sender, data)'
    # Data is (x_min, x_max, y_min, y_max).
    show_color_scale: bool = False
    scale_min: float = 0.0
    scale_max: float = 1.0
    scale_height: int = 100
    show: bool = True
    show_annotations: bool = True
    show_drag_lines: bool = True
    show_drag_points: bool = True

    @property
    def restrict_types(self) -> t.Tuple:
        from .plot_types import PlotType
        return PlotType,

    @property
    @util.CacheResult
    def children(self) -> t.Dict[str, "PlotType"]:
        from .plot_types import PlotType

        # get children from super
        # noinspection PyTypeChecker
        _children = super().children  # type: t.Dict[str, PlotType]

        # let us change key to name
        # note that the key is `item[...]` format as this is widget container
        # but for PlotType we can safely use name
        # Note that the actual keys from super will be unique but we need to
        # make that sure for `PlotType.name`
        _ret = {}
        for k, v in _children.items():
            # check if item is PlotType
            if not isinstance(v, PlotType):
                e.code.CodingError(
                    msgs=[
                        f"We expect you to add only items of type {PlotType} "
                        f"to {Plot}",
                        f"Found unsupported type {type(v)}"
                    ]
                )
            # add to dict with new key
            if v.name not in _ret.keys():
                _ret[v.name] = v
            else:
                e.code.CodingError(
                    msgs=[
                        f"The name `{v.name}` is repeated while adding items to "
                        f"WidgetContainer {Plot}"
                    ]
                )

        # return
        return _ret

    def make_gui(self):
        # ------------------------------------------------ 01
        # resolve if query callback overridden
        if self.__class__.query_callback != Plot.query_callback:
            _query_callback = self.query_callback
        else:
            _query_callback = None

        # ------------------------------------------------ 02
        # call add plot
        dpgc.add_plot(
            name=self.id,
            parent=self.parent_id,
            x_axis_name=self.x_axis_name,
            y_axis_name=self.y_axis_name,
            no_legend=self.no_legend,
            no_menus=self.no_menus,
            no_box_select=self.no_box_select,
            no_mouse_pos=self.no_mouse_pos,
            no_highlight=self.no_highlight,
            no_child=self.no_child,
            query=self.query,
            crosshairs=self.crosshairs,
            anti_aliased=self.anti_aliased,
            equal_aspects=self.equal_aspects,
            yaxis2=self.yaxis2,
            yaxis3=self.yaxis3,
            xaxis_no_gridlines=self.xaxis_no_gridlines,
            xaxis_no_tick_marks=self.xaxis_no_tick_marks,
            xaxis_no_tick_labels=self.xaxis_no_tick_labels,
            xaxis_log_scale=self.xaxis_log_scale,
            xaxis_time=self.xaxis_time,
            xaxis_invert=self.xaxis_invert,
            xaxis_lock_min=self.xaxis_lock_min,
            xaxis_lock_max=self.xaxis_lock_max,
            yaxis_no_gridlines=self.yaxis_no_gridlines,
            yaxis_no_tick_marks=self.yaxis_no_tick_marks,
            yaxis_no_tick_labels=self.yaxis_no_tick_labels,
            yaxis_log_scale=self.yaxis_log_scale,
            yaxis_invert=self.yaxis_invert,
            yaxis_lock_min=self.yaxis_lock_min,
            yaxis_lock_max=self.yaxis_lock_max,
            y2axis_no_gridlines=self.y2axis_no_gridlines,
            y2axis_no_tick_marks=self.y2axis_no_tick_marks,
            y2axis_no_tick_labels=self.y2axis_no_tick_labels,
            y2axis_log_scale=self.y2axis_log_scale,
            y2axis_invert=self.y2axis_invert,
            y2axis_lock_min=self.y2axis_lock_min,
            y2axis_lock_max=self.y2axis_lock_max,
            y3axis_no_gridlines=self.y3axis_no_gridlines,
            y3axis_no_tick_marks=self.y3axis_no_tick_marks,
            y3axis_no_tick_labels=self.y3axis_no_tick_labels,
            y3axis_log_scale=self.y3axis_log_scale,
            y3axis_invert=self.y3axis_invert,
            y3axis_lock_min=self.y3axis_lock_min,
            y3axis_lock_max=self.y3axis_lock_max,
            before=self.before,
            width=self.width,
            height=self.height,
            show_color_scale=self.show_color_scale,
            scale_min=self.scale_min,
            scale_max=self.scale_max,
            scale_height=self.scale_height,
            label=self.label,
            show=self.show,
            show_annotations=self.show_annotations,
            show_drag_lines=self.show_drag_lines,
            show_drag_points=self.show_drag_points,
            query_callback=_query_callback
        )

        # ------------------------------------------------ 03
        # make children gui ... i.e. the items
        self.make_children_gui()

    # noinspection PyMethodMayBeStatic
    def query_callback(self, sender, data):
        e.code.CodingError(
            msgs=[
                f"Please override this method by subclassing the {Plot}, "
                f"in case you want to use query_callback"
            ]
        )

    def get_plot_xlimits(self) -> t.Tuple[float, float]:
        _ = dpgc.get_plot_xlimits(plot=self.id)
        return _[0], _[1]

    def get_plot_ylimits(self) -> t.Tuple[float, float]:
        _ = dpgc.get_plot_ylimits(plot=self.id)
        return _[0], _[1]

    def set_plot_xlimits(self, xmin: float, xmax: float):
        dpgc.set_plot_xlimits(plot=self.id, xmin=xmin, xmax=xmax)

    def set_plot_ylimits(self, ymin: float, ymax: float):
        dpgc.set_plot_ylimits(plot=self.id, ymin=ymin, ymax=ymax)

    def set_plot_xlimits_auto(self):
        dpgc.set_plot_xlimits_auto(plot=self.id)

    def set_plot_ylimits_auto(self):
        dpgc.set_plot_ylimits_auto(plot=self.id)

    def set_xticks(self, label_pairs: t.List[t.Tuple[str, float]]):
        dpgc.set_xticks(plot=self.id, label_pairs=label_pairs)

    def set_yticks(self, label_pairs: t.List[t.Tuple[str, float]]):
        dpgc.set_yticks(plot=self.id, label_pairs=label_pairs)

    def reset_xticks(self):
        dpgc.reset_xticks(plot=self.id)

    def reset_yticks(self):
        dpgc.reset_yticks(plot=self.id)

    def clear(self):
        dpgc.clear_plot(plot=self.id)

    def is_plot_queried(self) -> bool:
        return dpgc.is_plot_queried(plot=self.id)

    def set_color_map(self, color_map: PlotColorMap):
        dpgc.set_color_map(plot=self.id, map=color_map.dpg_value)

    def get_plot_query_area(self) -> t.Tuple[float, float, float, float]:
        # noinspection PyTypeChecker
        return dpgc.get_plot_query_area(plot=self.id)


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



