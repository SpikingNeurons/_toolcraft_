import abc
import dataclasses
import dearpygui.core as dpgc
import dearpygui.simple as dpgs
import typing as t
import numpy as np

from .. import error as e
from .__base__ import Color, PlotMarker, PLOT_DATA_TYPE, PLOT_LABEL_TYPE, Widget
from .widget import Plot


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
