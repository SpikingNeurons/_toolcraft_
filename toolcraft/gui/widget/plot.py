import abc
import dataclasses
import dearpygui.core as dpgc
import dearpygui.simple as dpgs
import typing as t
import enum
import numpy as np

from ... import error as e
from ... import util
from ..__base__ import Color, Widget, WidgetContainer

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]
PLOT_LABEL_TYPE = t.Union[t.List[str], np.ndarray]


class PlotColorMap(enum.Enum):
    """
    Refer to
    >>> dpgc.mvPlotColormap_Cool
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

    @property
    def dpg_value(self) -> int:
        try:
            return getattr(dpgc, f"mvPlotColormap_{self.name}")
        except AttributeError:
            e.code.NotSupported(
                msgs=[f"Unknown {self}"]
            )


class PlotMarker(enum.Enum):
    """
    Refer to
    >>> dpgc.mvPlotMarker_Asterisk
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

    @property
    def dpg_value(self) -> int:
        try:
            return getattr(dpgc, f"mvPlotMarker_{self.name}")
        except AttributeError:
            e.code.NotSupported(
                msgs=[f"Unknown {self}"]
            )


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
        return PlotType,

    @property
    @util.CacheResult
    def children(self) -> t.Dict[str, "PlotType"]:

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
class PlotType(Widget, abc.ABC):
    """
    todo: Need to implement delete for all Series. Check below method:
    >>> dpgc.delete_series
    """
    name: str


@dataclasses.dataclass(frozen=True)
class Annotation(PlotType):
    """
    Refer to
    >>> dpgc.add_annotation
    """
    text: str
    x: float
    y: float
    xoffset: float
    yoffset: float
    color: Color = Color.DEFAULT
    clamped: bool = True

    def make_gui(self):
        dpgc.add_annotation(
            plot=self.parent_id,
            text=self.text,
            x=self.x,
            y=self.y,
            xoffset=self.xoffset,
            yoffset=self.yoffset,
            color=self.color.dpg_value,
            clamped=self.clamped,
            # note that tag acts as name
            tag=self.name,
        )

    def delete(self):
        dpgc.delete_annotation(
            plot=self.parent_id,
            name=self.name,
        )


@dataclasses.dataclass(frozen=True)
class AreaSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_area_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    color: Color
    fill: Color
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_area_series(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            y=self.y,
            color=self.color.dpg_value,
            fill=self.fill.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class BarSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_bar_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    weight: float = 1.0
    horizontal: bool = False
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_bar_series(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            y=self.y,
            weight=self.weight,
            horizontal=self.horizontal,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class CandleSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_candle_series
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

    def make_gui(self):
        dpgc.add_candle_series(
            plot=self.parent_id,
            name=self.name,
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
class DragLine(PlotType):
    """
    Refer to
    >>> dpgc.add_drag_line
    """
    source: str = ""
    color: Color = Color.DEFAULT
    thickness: float = -1
    y_line: bool = False
    show_label: bool = True
    default_value: float = 0.0

    def make_gui(self):
        # if overridden get the callback
        _callback = None
        if DragLine.callback != self.__class__.callback:
            _callback = self.callback

        # add
        dpgc.add_drag_line(
            plot=self.parent_id,
            name=self.name,
            source=self.source,
            color=self.color.dpg_value,
            thickness=self.thickness,
            y_line=self.y_line,
            show_label=self.show_label,
            default_value=self.default_value,
            callback=_callback,
        )

    def delete(self):
        dpgc.delete_drag_line(
            plot=self.parent_id, name=self.name
        )

    # noinspection PyMethodMayBeStatic
    def callback(self, sender, data):
        e.code.NotAllowed(
            msgs=[
                f"In case you want to use callback override this method"
            ]
        )


@dataclasses.dataclass(frozen=True)
class DragPoint(PlotType):
    """
    Refer to
    >>> dpgc.add_drag_point
    """
    source: str = ""
    color: Color = Color.DEFAULT
    radius: float = 4.0
    show_label: bool = True
    default_x: float = 0.0
    default_y: float = 0.0

    def make_gui(self):
        # if overridden get the callback
        _callback = None
        if DragLine.callback != self.__class__.callback:
            _callback = self.callback

        # add
        dpgc.add_drag_point(
            plot=self.parent_id,
            name=self.name,
            source=self.source,
            color=self.color.dpg_value,
            radius=self.radius,
            show_label=self.show_label,
            default_x=self.default_x,
            default_y=self.default_y,
            callback=_callback,
        )

    def delete(self):
        dpgc.delete_drag_point(
            plot=self.parent_id, name=self.name
        )

    # noinspection PyMethodMayBeStatic
    def callback(self, sender, data):
        e.code.NotAllowed(
            msgs=[
                f"In case you want to use callback override this method"
            ]
        )


@dataclasses.dataclass(frozen=True)
class ErrorSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_error_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    negative: PLOT_DATA_TYPE
    positive: PLOT_DATA_TYPE
    horizontal: bool = False
    update_bounds: bool = True
    color: Color = Color.DEFAULT
    axis: int = 0

    def make_gui(self):
        dpgc.add_error_series(
            plot=self.parent_id,
            name=self.name,
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
class HeatSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_heat_series
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

    def make_gui(self):
        # noinspection PyTypeChecker
        dpgc.add_heat_series(
            plot=self.parent_id,
            name=self.name,
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
class HorizLineSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_hline_series
    """
    x: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_hline_series(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class ImageSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_image_series
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
    def make_gui(self):
        dpgc.add_image_series(
            plot=self.parent_id,
            name=self.name,
            value=self.value,
            bounds_min=self.bounds_min,
            bounds_max=self.bounds_max,
            uv_min=self.uv_min,
            uv_max=self.uv_max,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class LineSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_line_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_line_series(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            y=self.y,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )

    @staticmethod
    def generate_from_npy(
        data: np.ndarray,
        label: t.List[str],
        x_axis: np.ndarray = None
    ) -> t.List["LineSeries"]:
        # ---------------------------------------------- 01
        # validate if data is 2 dim
        if data.ndim != 2:
            e.code.CodingError(
                msgs=[
                    f"Expecting data to be 2D array",
                    f"Found ndim={data.ndim}"
                ]
            )
        # validate if lengths are correct
        if data.shape[1] != len(label):
            e.code.NotAllowed(
                msgs=[
                    f"The number of columns in data does not match to the "
                    f"number of labels ..."
                ]
            )
        # check x_axis and convert it if needed
        if isinstance(x_axis, np.ndarray):
            # length must be same
            if len(data) != len(x_axis):
                e.code.CodingError(
                    msgs=[
                        f"The length of data does not match the length of "
                        f"x_axis",
                        f"{len(data)}!={len(x_axis)}"
                    ]
                )
            # if x_axis is 2D then it should match the columns
            if x_axis.ndim == 2:
                if x_axis.shape[1] != data.shape[1]:
                    e.code.NotAllowed(
                        msgs=[
                            f"When using 2D x_axis the columns should equal "
                            f"number of columns in data"
                        ]
                    )
        elif x_axis is None:
            x_axis = np.arange(data.shape[0])

        # ---------------------------------------------- 02
        # loop over columns and generate series
        _ret = []
        for _column_id in range(data.shape[1]):
            _ret.append(
                LineSeries(
                    name=label[_column_id],
                    x=x_axis if x_axis.ndim == 1 else x_axis[:, _column_id],
                    y=data[:, _column_id].copy()
                )
            )

        # ---------------------------------------------- 04
        # return
        return _ret


@dataclasses.dataclass(frozen=True)
class PieSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_pie_series
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

    def make_gui(self):
        dpgc.add_pie_series(
            plot=self.parent_id,
            name=self.name,
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
class ScatterSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_scatter_series
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

    def make_gui(self):
        dpgc.add_scatter_series(
            plot=self.parent_id,
            name=self.name,
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
        data: np.ndarray,
        label: np.ndarray,
        label_formatter: str,
    ) -> t.List["ScatterSeries"]:
        # ---------------------------------------------- 01
        # validate if lengths are correct
        if len(data) != len(label):
            e.code.NotAllowed(
                msgs=[
                    f"The data and label are not of same length ..."
                ]
            )
        # validate if data is 2 dim
        if data.ndim != 2:
            e.code.CodingError(
                msgs=[
                    f"Expecting data to be 2D array",
                    f"Found ndim={data.ndim}"
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
            _data_filtered = data[label == _label]

            # get formatted label
            _label_formatted = label_formatter.format(label=_label)

            # create and append
            _ret.append(
                ScatterSeries(
                    name=_label_formatted,
                    x=_data_filtered[:, 0].copy(),
                    y=_data_filtered[:, 1].copy(),
                ),
            )

        # ---------------------------------------------- 04
        # return
        return _ret


@dataclasses.dataclass(frozen=True)
class ShadeSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_shade_series
    """

    x: PLOT_DATA_TYPE
    y1: PLOT_DATA_TYPE
    y2: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    fill: Color = Color.DEFAULT
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_shade_series(
            plot=self.parent_id,
            name=self.name,
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
class StairSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_stair_series
    """

    x: PLOT_DATA_TYPE
    y: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.0
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_stair_series(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            y=self.y,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class StemSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_stem_series
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

    def make_gui(self):
        dpgc.add_stem_series(
            plot=self.parent_id,
            name=self.name,
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
class TextPoint(PlotType):
    """
    Refer to
    >>> dpgc.add_text_point
    """

    x: float
    y: float
    vertical: bool = False
    xoffset: int = 0.
    yoffset: int = 0.
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_text_point(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            y=self.y,
            xoffset=self.xoffset,
            yoffset=self.yoffset,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )


@dataclasses.dataclass(frozen=True)
class VertLineSeries(PlotType):
    """
    Refer to
    >>> dpgc.add_vline_series
    """
    x: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.
    update_bounds: bool = True
    axis: int = 0

    def make_gui(self):
        dpgc.add_vline_series(
            plot=self.parent_id,
            name=self.name,
            x=self.x,
            color=self.color.dpg_value,
            weight=self.weight,
            update_bounds=self.update_bounds,
            axis=self.axis,
        )
