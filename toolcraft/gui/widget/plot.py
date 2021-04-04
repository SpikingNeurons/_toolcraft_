import abc
import dataclasses
import dearpygui.core as dpg
import typing as t
import enum
import numpy as np

from ... import error as e
from ... import util
from ... import marshalling as m
from .. import Color, Widget, Callback

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]
PLOT_LABEL_TYPE = t.Union[t.List[str], np.ndarray]


class PlotColorMap(m.FrozenEnum, enum.Enum):
    """
    Refer to
    >>> dpg.mvPlotColormap_Cool
    """
    Cool = enum.auto()
    Dark = enum.auto()
    Deep = enum.auto()
    Default = enum.auto()
    Hot = enum.auto()
    Jet = enum.auto()
    Paired = enum.auto()
    Pastel = enum.auto()
    Pink = enum.auto()
    Plasma = enum.auto()
    Viridis = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_plot_color_map"

    @property
    def dpg_value(self) -> int:
        try:
            return getattr(dpg, f"mvPlotColormap_{self.name}")
        except AttributeError:
            e.code.NotSupported(
                msgs=[f"Unknown {self}"]
            )


class PlotMarker(m.FrozenEnum, enum.Enum):
    """
    Refer to
    >>> dpg.mvPlotMarker_Asterisk
    """
    Asterisk = enum.auto()
    Circle = enum.auto()
    Cross = enum.auto()
    Diamond = enum.auto()
    Down = enum.auto()
    Left = enum.auto()
    Null = enum.auto()
    Plus = enum.auto()
    Right = enum.auto()
    Square = enum.auto()
    Up = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_plot_marker"

    @property
    def dpg_value(self) -> int:
        try:
            return getattr(dpg, f"mvPlotMarker_{self.name}")
        except AttributeError:
            e.code.NotSupported(
                msgs=[f"Unknown {self}"]
            )


@dataclasses.dataclass(frozen=True)
class _SimplePlot(Widget):
    """
    Refer to
    >>> dpg.add_simple_plot
    todo: instead of add_simple_plot make you own SimplePlot derived from Plot
      This is because we connot plot with build() as value is needed
    """
    overlay: str = ""
    minscale: float = 0.0
    maxscale: float = 0.0
    histogram: bool = False
    tip: str = ""
    width: int = 0
    height: int = 0
    source: str = ""
    label: str = ""
    show: bool = True

    @property
    def is_container(self) -> bool:
        return False

    def build(
        self,
        guid: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
        # there is nothing to do here as it will happen when you call plot()
        ...

    def plot(self, value: PLOT_DATA_TYPE, before: str = ""):
        dpg.add_simple_plot(
            **self.internal.dpg_kwargs,
            value=value,
            overlay=self.overlay,
            minscale=self.minscale,
            maxscale=self.maxscale,
            histogram=self.histogram,
            tip=self.tip,
            width=self.width,
            height=self.height,
            source=self.source,
            label=self.label,
            show=self.show,
        )


@dataclasses.dataclass(frozen=True)
class Plot(Widget):
    """
    Refer to
    >>> dpg.add_plot
    """
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
    parent: str = ''
    width: int = -1
    height: int = -1
    show_color_scale: bool = False
    scale_min: float = 0.0
    scale_max: float = 1.0
    scale_height: int = 100
    show: bool = True
    show_annotations: bool = True
    show_drag_lines: bool = True
    show_drag_points: bool = True
    # Callback ran when plot is queried. Should be of the form
    # 'def Callback(sender, data)'
    # Data is (x_min, x_max, y_min, y_max).
    query_callback: Callback = None

    @property
    def is_container(self) -> bool:
        return False

    @property
    @util.CacheResult
    def items(self) -> t.Dict[str, "PlotItem"]:
        return {}

    def delete_items(self, items: t.Union[str, t.List[str]]):
        """
        Here we delete PlotItem in items
        """
        # make it list if needed
        if not isinstance(items, list):
            items = [items]

        # loop over items
        for item in items:
            self.items[item].delete()

    def add_items(self, items: t.Union["PlotItem", t.List["PlotItem"]]):
        # make it list if needed
        if not isinstance(items, list):
            items = [items]

        # loop over items
        for item in items:

            # todo: Who should be sender widget of callbacks in PlotType?
            #   Note that PlotType are not Widget so we cannot have them as
            #   sender as they do not inherit `Widget.id` mechanism
            # todo: We might need to do immutable copy for this callback similar
            #  to Widget class
            # todo: may be this needs to go in build_pre_runner or build
            if isinstance(item, (DragLine, DragPoint)):
                if item.callback is not None:
                    e.code.NotSupported(
                        msgs=[
                            f"We are yet to figure this out. That is how to "
                            f"handle Callback in PlotType which is not a Widget"
                        ]
                    )
                    item.callback.set_sender(sender=self)

            # if item not in items add it else raise error
            if item.label in self.items.keys():
                e.code.NotAllowed(
                    msgs=[
                        f"Looks like you have already added item with "
                        f"label {item.label}"
                    ]
                )
            else:
                self.items[item.label] = item

            # if the self is already built then we need to plot this item
            if self.internal.is_build_done:
                item.plot(parent_plot=self)

    def build(
        self,
        guid: str,
        parent: "Widget",
        before: t.Optional["Widget"] = None,
    ):
        # call add plot
        dpg.add_plot(
            **self.internal.dpg_kwargs,
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
            query_callback=None if self.query_callback is None else
            self.query_callback.fn
        )

        # if there are items plot them as we will not do that during
        # add_items if the self is not built
        for item in self.items.values():
            item.plot(parent_plot=self)

    def get_plot_xlimits(self) -> t.Tuple[float, float]:
        _ = dpg.get_plot_xlimits(plot=self.id)
        return _[0], _[1]

    def get_plot_ylimits(self) -> t.Tuple[float, float]:
        _ = dpg.get_plot_ylimits(plot=self.id)
        return _[0], _[1]

    def set_plot_xlimits(self, xmin: float, xmax: float):
        dpg.set_plot_xlimits(plot=self.id, xmin=xmin, xmax=xmax)

    def set_plot_ylimits(self, ymin: float, ymax: float):
        dpg.set_plot_ylimits(plot=self.id, ymin=ymin, ymax=ymax)

    def set_plot_xlimits_auto(self):
        dpg.set_plot_xlimits_auto(plot=self.id)

    def set_plot_ylimits_auto(self):
        dpg.set_plot_ylimits_auto(plot=self.id)

    def set_xticks(self, label_pairs: t.List[t.Tuple[str, float]]):
        dpg.set_xticks(plot=self.id, label_pairs=label_pairs)

    def set_yticks(self, label_pairs: t.List[t.Tuple[str, float]]):
        dpg.set_yticks(plot=self.id, label_pairs=label_pairs)

    def reset_xticks(self):
        dpg.reset_xticks(plot=self.id)

    def reset_yticks(self):
        dpg.reset_yticks(plot=self.id)

    def clear(self):
        dpg.clear_plot(plot=self.id)

    def is_plot_queried(self) -> bool:
        return dpg.is_plot_queried(plot=self.id)

    def set_color_map(self, color_map: PlotColorMap):
        dpg.set_color_map(plot=self.id, map=color_map.dpg_value)

    def get_plot_query_area(self) -> t.Tuple[float, float, float, float]:
        # noinspection PyTypeChecker
        return dpg.get_plot_query_area(plot=self.id)


@dataclasses.dataclass(frozen=True)
class PlotItem(abc.ABC):
    """
    Note that this is not a Widget nor a m.HashableClass as this will reprent
    data that we will plot and there is no need to serialize it.
    todo: Need to implement delete for all Series. Check below method:
    >>> dpg.delete_series
    """
    # This basically behaves like guid but we keep it as label so that users
    # can even add spaces or special characters inside label
    # Note that unlike guid they will be displayed in plot.
    # Also may be we can directly get latex expressions here :)
    # So guid for PlotItem is not sensible
    label: str

    def __post_init__(self):
        """
        We do it here as we cannot use HashableClass here as the fields can
        have complex data that might not be possible to serialize as yaml
        """
        self.init_validate()
        self.init()

    def init_validate(self):
        ...

    def init(self):
        ...

    @abc.abstractmethod
    def plot(self, parent_plot: Plot):
        ...

    def delete(self):
        e.code.NotSupported(
            msgs=[f"please implement delete for {self.__class__}"])


@dataclasses.dataclass(frozen=True)
class Annotation(PlotItem):
    """
    Refer to
    >>> dpg.add_annotation
    """
    text: str
    x: float
    y: float
    xoffset: float
    yoffset: float
    color: Color = Color.DEFAULT
    clamped: bool = True

    def plot(self, parent_plot: Plot):
        dpg.add_annotation(
            plot=parent_plot.name,
            text=self.text,
            x=self.x,
            y=self.y,
            xoffset=self.xoffset,
            yoffset=self.yoffset,
            color=self.color.dpg_value,
            clamped=self.clamped,
            # note that tag acts as name
            tag=self.label,
        )


@dataclasses.dataclass(frozen=True)
class AreaSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_area_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    color: Color
    fill: Color
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_area_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            color=self.color.dpg_value,
            fill=self.fill.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class BarSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_bar_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    weight: float = 1.0
    horizontal: bool = False
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_bar_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            weight=self.weight,
            horizontal=self.horizontal,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class CandleSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_candle_series
    """

    date: PLOT_DATA_TYPE
    opens: PLOT_DATA_TYPE
    highs: PLOT_DATA_TYPE
    lows: PLOT_DATA_TYPE
    closes: PLOT_DATA_TYPE
    tooltip: bool = True
    bull_color: Color = Color.CUSTOM(0., 255., 113., 255.)
    bear_color: Color = Color.CUSTOM(218., 13., 79., 255.)
    weight: float = 0.25
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_candle_series(
            plot=parent_plot.name,
            name=self.label,
            date=self.date,
            opens=self.opens,
            highs=self.highs,
            lows=self.lows,
            closes=self.closes,
            tooltip=self.tooltip,
            bull_color=self.bull_color.dpg_value,
            bear_color=self.bear_color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class DragLine(PlotItem):
    """
    Refer to
    >>> dpg.add_drag_line
    """
    source: str = ""
    color: Color = Color.DEFAULT
    thickness: float = -1
    y_line: bool = False
    show_label: bool = True
    default_value: float = 0.0
    callback: Callback = None

    def plot(self, parent_plot: Plot):

        # add
        dpg.add_drag_line(
            plot=parent_plot.name,
            name=self.label,
            source=self.source,
            color=self.color.dpg_value,
            thickness=self.thickness,
            y_line=self.y_line,
            show_label=self.show_label,
            default_value=self.default_value,
            callback=None if self.callback is None else self.callback.fn,
        )

    def delete(self):
        e.code.NotSupported(msgs=["figure it out"])
        dpg.delete_drag_line(
            plot=..., name=self.label
        )


@dataclasses.dataclass(frozen=True)
class DragPoint(PlotItem):
    """
    Refer to
    >>> dpg.add_drag_point
    """
    source: str = ""
    color: Color = Color.DEFAULT
    radius: float = 4.0
    show_label: bool = True
    default_x: float = 0.0
    default_y: float = 0.0
    callback: Callback = None

    def plot(self, parent_plot: Plot):

        # add
        dpg.add_drag_point(
            plot=parent_plot.name,
            name=self.label,
            source=self.source,
            color=self.color.dpg_value,
            radius=self.radius,
            show_label=self.show_label,
            default_x=self.default_x,
            default_y=self.default_y,
            callback=None if self.callback is None else self.callback.fn,
        )

    def delete(self):
        e.code.NotSupported(msgs=["figure it out"])
        dpg.delete_drag_point(
            plot=..., name=self.label
        )


@dataclasses.dataclass(frozen=True)
class ErrorSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_error_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    negative: PLOT_DATA_TYPE
    positive: PLOT_DATA_TYPE
    horizontal: bool = False
    update_bounds: bool = True
    color: Color = Color.DEFAULT
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_error_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            negative=self.negative,
            positive=self.positive,
            horizontal=self.horizontal,
            update_bounds=self.update_bounds,
            color=self.color.dpg_value,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class HeatSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_heat_series
    """

    values: PLOT_DATA_TYPE
    rows: int
    columns: int
    scale_min: float
    scale_max: float
    format: str = '%0.1f'
    bounds_min: t.Tuple[float, float] = (0., 0.)
    bounds_max: t.Tuple[float, float] = (1., 1.)
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        # noinspection PyTypeChecker
        dpg.add_heat_series(
            plot=parent_plot.name,
            name=self.label,
            values=self.values,
            rows=self.rows,
            columns=self.columns,
            scale_min=self.scale_min,
            scale_max=self.scale_max,
            format=self.format,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class HorizLineSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_hline_series
    """
    x: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_hline_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class ImageSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_image_series
    """
    value: str
    # bottom left coordinate
    bounds_min: t.Tuple[float, float]
    # top right coordinate
    bounds_max: t.Tuple[float, float]
    # normalized texture coordinates
    uv_min: t.Tuple[float, float] = (0., 0.)
    # normalized texture coordinates
    uv_max: t.Tuple[float, float] = (1., 1.)
    tint_color: Color = Color.WHITE
    update_bounds: bool = True
    axis: int = 0

    # noinspection PyTypeChecker
    def plot(self, parent_plot: Plot):
        dpg.add_image_series(
            plot=parent_plot.name,
            name=self.label,
            value=self.value,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            uv_min=self.uv_min,
            uv_max=self.uv_max,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class LineSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_line_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_line_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )

    @staticmethod
    def generate_from_npy(
        data: t.List[np.ndarray],
        label: t.List[str],
        x_axis: t.List[np.ndarray] = None
    ) -> t.List["LineSeries"]:
        # ---------------------------------------------- 01
        # validate length of lists
        if len(data) != len(label):
            e.code.NotAllowed(
                msgs=[
                    f"We expect same number of items in data and label"
                ]
            )
        if x_axis is not None:
            if len(x_axis) != len(label):
                e.code.NotAllowed(
                    msgs=[
                        f"We expect same number of items in x_axis and label"
                    ]
                )
        # ---------------------------------------------- 02
        # loop over and generate series
        _ret = []
        for _index in range(len(label)):
            # get data for index
            _label = label[_index]
            _data = data[_index]
            _length = len(_data)
            if x_axis is not None:
                _x_axis = x_axis[_index]
            else:
                _x_axis = np.arange(_length)

            # validate
            if _data.ndim != 1:
                e.code.NotAllowed(
                    msgs=[
                        f"We expect data to be 1D for index {_index}"
                    ]
                )
            if _x_axis.shape != _data.shape:
                e.code.NotAllowed(
                    msgs=[
                        f"We were expecting x_axis and data to have same "
                        f"shape. Check item {_index}",
                        {
                            '_x_axis': _x_axis.shape,
                            '_data': _data.shape
                        }
                    ]
                )

            # create series
            _ret.append(
                LineSeries(
                    label=_label, x=_x_axis, y=_data
                )
            )

        # ---------------------------------------------- 03
        # return
        return _ret


@dataclasses.dataclass(frozen=True)
class PieSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_pie_series
    """

    values: PLOT_DATA_TYPE
    labels: PLOT_LABEL_TYPE
    x: float
    y: float
    radius: float
    normalize: bool = False
    angle: float = 90.
    format: str = '%0.2f'
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_pie_series(
            plot=parent_plot.name,
            name=self.label,
            values=self.values,
            labels=self.labels,
            x=self.x,
            y=self.y,
            radius=self.radius,
            normalize=self.normalize,
            angle=self.angle,
            format=self.format,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class ScatterSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_scatter_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    marker: PlotMarker = PlotMarker.Circle
    size: float = 4.0
    weight: float = 1.0
    outline: Color = Color.DEFAULT
    fill: Color = Color.DEFAULT
    update_bounds: bool = True
    # split x and y
    xy_data_format: bool = False
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_scatter_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            marker=self.marker.dpg_value,
            size=self.size,
            weight=self.weight,
            outline=self.outline.dpg_value,
            fill=self.fill.dpg_value,
            update_bounds=self.update_bounds,
            xy_data_format=self.xy_data_format,
            axis=self.axis,
        )

    @staticmethod
    def generate_from_npy(
        data_x: np.ndarray,
        data_y: np.ndarray,
        label: np.ndarray,
        label_formatter: str,
        size: float = 4.0,
    ) -> t.List["ScatterSeries"]:
        # ---------------------------------------------- 01
        # validate if lengths are correct
        if data_x.shape != label.shape:
            e.code.NotAllowed(
                msgs=[
                    f"The data_x and label are not of same length ..."
                ]
            )
        if data_y.shape != label.shape:
            e.code.NotAllowed(
                msgs=[
                    f"The data_y and label are not of same length ..."
                ]
            )
        if data_x.ndim != 1:
            e.code.NotAllowed(
                msgs=[
                    f"We expect data_x to be 1D"
                ]
            )
        if data_y.ndim != 1:
            e.code.NotAllowed(
                msgs=[
                    f"We expect data_y to be 1D"
                ]
            )
        if label.ndim != 1:
            e.code.NotAllowed(
                msgs=[
                    f"We expect label to be 1D"
                ]
            )

        # ---------------------------------------------- 02
        # estimate unique labels
        _labels = np.unique(label)

        # ---------------------------------------------- 03
        # loop over categories and generate series
        _ret = []
        for _label in _labels:
            # filter data to plot for this label
            _filter = label == _label
            _data_x_filtered = data_x[_filter]
            _data_y_filtered = data_y[_filter]

            # get formatted label
            _label_formatted = label_formatter.format(label=_label)

            # create and append
            _ret.append(
                ScatterSeries(
                    label=_label_formatted,
                    x=_data_x_filtered,
                    y=_data_y_filtered,
                    size=size,
                ),
            )

        # ---------------------------------------------- 04
        # return
        return _ret


@dataclasses.dataclass(frozen=True)
class ShadeSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_shade_series
    """

    x: PLOT_DATA_TYPE
    y1: PLOT_DATA_TYPE
    y2: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    fill: Color = Color.DEFAULT
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_shade_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y1=self.y1,
            y2=self.y2,
            color=self.color.dpg_value,
            fill=self.fill.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class StairSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_stair_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_stair_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class StemSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_stem_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    marker: PlotMarker = PlotMarker.Circle
    size: float = 4.0
    weight: float = 1.0
    outline: Color = Color.DEFAULT
    fill: Color = Color.DEFAULT
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_stem_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            marker=self.marker.dpg_value,
            size=self.size,
            weight=self.weight,
            outline=self.outline.dpg_value,
            fill=self.fill.dpg_value,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class TextPoint(PlotItem):
    """
    Refer to
    >>> dpg.add_text_point
    """

    x: float
    y: float
    vertical: bool = False
    xoffset: int = 0.
    yoffset: int = 0.
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_text_point(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            y=self.y,
            xoffset=self.xoffset,
            yoffset=self.yoffset,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class VertLineSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_vline_series
    """
    x: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.
    update_bounds: bool = True
    axis: int = 0

    def plot(self, parent_plot: Plot):
        dpg.add_vline_series(
            plot=parent_plot.name,
            name=self.label,
            x=self.x,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )
