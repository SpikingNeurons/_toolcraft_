import abc
import dataclasses
import dearpygui.dearpygui as dpg
import dearpygui.core as internal_dpg
import typing as t
import enum
import numpy as np

from ... import error as e
from ... import util
from ... import marshalling as m
from .. import Color, Widget, Callback
from .. import helper

PLOT_DATA_TYPE = t.Union[t.List[float], np.ndarray]


class ColorMap(m.FrozenEnum, enum.Enum):
    """
    Refer:
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
    def dpg_id(self) -> int:
        return _DPG_IDS_COLOR_MAP[self]


_DPG_IDS_COLOR_MAP = helper.extract_dpg_ids(
    enum_class=ColorMap, dpg_prefix="mvPlotColormap_")


class Marker(m.FrozenEnum, enum.Enum):
    """
    Refer:
    >>> dpg.mvPlotMarker_Asterisk
    """
    NONE = enum.auto()
    Asterisk = enum.auto()
    Circle = enum.auto()
    Cross = enum.auto()
    Diamond = enum.auto()
    Down = enum.auto()
    Left = enum.auto()
    Plus = enum.auto()
    Right = enum.auto()
    Square = enum.auto()
    Up = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_plot_marker"

    @property
    def dpg_id(self) -> int:
        return _DPG_IDS_MARKER[self]


_DPG_IDS_MARKER = helper.extract_dpg_ids(
    enum_class=Marker, dpg_prefix="mvPlotMarker_")


class Location(m.FrozenEnum, enum.Enum):
    """
    Refer:
    >>> dpg.mvPlot_Location_Center
    """
    Center = enum.auto()
    North = enum.auto()
    South = enum.auto()
    West = enum.auto()
    East = enum.auto()
    NorthWest = enum.auto()
    NorthEast = enum.auto()
    SouthWest = enum.auto()
    SouthEast = enum.auto()

    @classmethod
    def yaml_tag(cls) -> str:
        return f"!gui_plot_location"

    @property
    def dpg_id(self) -> int:
        return _DPG_IDS_LOCATION[self]


_DPG_IDS_LOCATION = helper.extract_dpg_ids(
    enum_class=Location, dpg_prefix="mvPlot_Location_")


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


# noinspection PyDefaultArgument
@dataclasses.dataclass(frozen=True)
class Plot(Widget):
    """
    Refer:
    >>> dpg.plot

    Adds a plot which is used to hold series, and can be drawn to with
    draw commands.
    """
    # ...
    legend: t.Optional[Legend] = "legend"

    # ...
    x_axis: t.Union[str, XAxis] = ""

    # ...
    y1_axis: t.Union[str, YAxis] = ""

    # ...
    y2_axis: t.Union[str, YAxis] = None

    # ...
    y3_axis: t.Union[str, YAxis] = None

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

    def init(self):

        # call super
        super().init()

        # add legend and axis which are same as widgets but are immediate
        # part of Plot widget and needs to be added well in advance
        if self.legend is not None:
            self.add_child(
                guid="_l",
                widget=Legend(label=self.legend)
                if isinstance(self.legend, str) else self.legend
            )
        if self.x_axis is not None:
            self.add_child(
                guid="_x",
                widget=XAxis(label=self.x_axis)
                if isinstance(self.x_axis, str) else self.x_axis
            )
        if self.y1_axis is not None:
            self.add_child(
                guid="_y1",
                widget=YAxis(label=self.y1_axis)
                if isinstance(self.y1_axis, str) else self.y1_axis
            )
        if self.y2_axis is not None:
            self.add_child(
                guid="_y2",
                widget=YAxis(label=self.y2_axis)
                if isinstance(self.y2_axis, str) else self.y2_axis
            )
        if self.y3_axis is not None:
            self.add_child(
                guid="_y3",
                widget=YAxis(label=self.y3_axis)
                if isinstance(self.y3_axis, str) else self.y3_axis
            )

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

    def get_y_axis(self, axis_dim: int) -> YAxis:
        if axis_dim not in [1, 2, 3]:
            e.code.CodingError(
                msgs=[
                    f"for y axis axis_dim should be one of {[1, 2, 3]} ... "
                    f"but found unsupported {axis_dim}"
                ]
            )
        try:
            # noinspection PyTypeChecker
            return self.children[f"_y{axis_dim}"]
        except KeyError:
            e.validation.NotAllowed(
                msgs=[
                    f"field `y{axis_dim}_axis` is not supplied"
                ]
            )

    def get_x_axis(self) -> XAxis:
        try:
            # noinspection PyTypeChecker
            return self.children["_x"]
        except KeyError:
            e.validation.NotAllowed(
                msgs=[
                    "field `x_axis` is not supplied"
                ]
            )

    def get_legend(self) -> Legend:
        try:
            # noinspection PyTypeChecker
            return self.children["_l"]
        except KeyError:
            e.validation.NotAllowed(
                msgs=[
                    f"field `legend` is not supplied"
                ]
            )

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

    def add_multi_label_series(
        self, *,
        data_x: np.ndarray,
        data_y: np.ndarray,
        label: np.ndarray,
        label_formatter: str,
        series_type: str,
        y_axis_dim: int = 1,
    ):
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

            # add series
            getattr(self, f"add_{series_type}")(
                label=_label_formatted,
                x=_data_x_filtered,
                y=_data_y_filtered,
                y_axis_dim=y_axis_dim,
            )

        # ---------------------------------------------- 04
        # return
        return _ret

    def add_area_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        fill: t.List[int] = (0, 0, 0, -255),
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_area_series

        Adds an area series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            fill:
              ...
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_area_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            fill=fill,
            contribute_to_bounds=contribute_to_bounds,
        )

    def add_bar_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        weight: float = 1.0,
        horizontal: bool = False,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_bar_series

        Adds a bar series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            weight:
              ...
            horizontal:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_bar_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            weight=weight,
            horizontal=horizontal,
        )

    def add_candle_series(
        self, *,
        dates: PLOT_DATA_TYPE,
        opens: PLOT_DATA_TYPE,
        closes: PLOT_DATA_TYPE,
        lows: PLOT_DATA_TYPE,
        highs: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        bull_color: t.List[int] = (0, 255, 113, 255),
        bear_color: t.List[int] = (218, 13, 79, 255),
        weight: int = 0.25,
        tooltip: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_candle_series

        Adds a candle series to a plot.

        Args:
            dates:
              ...
            opens:
              ...
            closes:
              ...
            lows:
              ...
            highs:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            bull_color:
              ...
            bear_color:
              ...
            weight:
              ...
            tooltip:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_candle_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            dates=dates,
            opens=opens,
            closes=closes,
            lows=lows,
            highs=highs,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            bull_color=bull_color,
            bear_color=bear_color,
            weight=weight,
            tooltip=tooltip,
        )

    def add_drag_line(
        self, *,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        user_data: t.Any = None,
        default_value: t.Any = 0.0,
        color: t.List[int] = (0, 0, 0, -255),
        thickness: float = 1.0,
        show_label: bool = True,
        vertical: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_drag_line

        Adds a drag line to a plot.

        Args:
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            callback:
              Registers a callback.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            default_value:
              ...
            color:
              ...
            thickness:
              ...
            show_label:
              ...
            vertical:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_drag_line(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            user_data=user_data,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
            vertical=vertical,
        )

    def add_drag_point(
        self, *,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        user_data: t.Any = None,
        default_value: t.Any = (0.0, 0.0),
        color: t.List[int] = (0, 0, 0, -255),
        thickness: float = 1.0,
        show_label: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_drag_point

        Adds a drag point to a plot.

        Args:
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            callback:
              Registers a callback.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            default_value:
              ...
            color:
              ...
            thickness:
              ...
            show_label:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_drag_point(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            user_data=user_data,
            default_value=default_value,
            color=color,
            thickness=thickness,
            show_label=show_label,
        )

    def add_error_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        negative: PLOT_DATA_TYPE,
        positive: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        contribute_to_bounds: bool = True,
        horizontal: bool = False,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_error_series

        Adds an error series to a plot.

        Args:
            x:
              ...
            y:
              ...
            negative:
              ...
            positive:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            contribute_to_bounds:
              ...
            horizontal:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_error_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            negative=negative,
            positive=positive,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            contribute_to_bounds=contribute_to_bounds,
            horizontal=horizontal,
        )

    def add_heat_series(
        self, *,
        x: PLOT_DATA_TYPE,
        rows: int,
        cols: int,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        scale_min: float = 0.0,
        scale_max: float = 1.0,
        bounds_min: t.Any = (0.0, 0.0),
        bounds_max: t.Any = (1.0, 1.0),
        format: str = '%0.1f',
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_heat_series

        Adds a heat series to a plot. Typically a color scale widget is also
        added to show the legend.

        Args:
            x:
              ...
            rows:
              ...
            cols:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            scale_min:
              Sets the color scale min. Typically paired with the color
              scale widget scale_min.
            scale_max:
              Sets the color scale max. Typically paired with the color
              scale widget scale_max.
            bounds_min:
              ...
            bounds_max:
              ...
            format:
              ...
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_heat_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            rows=rows,
            cols=cols,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            scale_min=scale_min,
            scale_max=scale_max,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            format=format,
            contribute_to_bounds=contribute_to_bounds,
        )

    def add_histogram_series(
        self, *,
        x: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        bins: int = -1,
        bar_scale: float = 1.0,
        min_range: float = 0.0,
        max_range: float = 1.0,
        cumlative: bool = False,
        density: bool = False,
        outliers: bool = True,
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_histogram_series

        Adds a histogram series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            bins:
              ...
            bar_scale:
              ...
            min_range:
              ...
            max_range:
              ...
            cumlative:
              ...
            density:
              ...
            outliers:
              ...
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_histogram_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            bins=bins,
            bar_scale=bar_scale,
            min_range=min_range,
            max_range=max_range,
            cumlative=cumlative,
            density=density,
            outliers=outliers,
            contribute_to_bounds=contribute_to_bounds,
        )

    def add_hline_series(
        self, *,
        x: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        contribute_to_bounds: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_hline_series

        Adds a infinite horizontal line series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            contribute_to_bounds:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_hline_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            contribute_to_bounds=contribute_to_bounds,
        )

    def add_image_series(
        self, *,
        texture_id: int,
        bounds_min: PLOT_DATA_TYPE,
        bounds_max: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        uv_min: t.List[float] = (0.0, 0.0),
        uv_max: t.List[float] = (1.0, 1.0),
        tint_color: t.List[int] = (255, 255, 255, 255),
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_image_series

        Adds a image series to a plot.

        Args:
            texture_id:
              ...
            bounds_min:
              ...
            bounds_max:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            uv_min:
              normalized texture coordinates
            uv_max:
              normalized texture coordinates
            tint_color:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_image_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            texture_id=texture_id,
            bounds_min=bounds_min,
            bounds_max=bounds_max,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            uv_min=uv_min,
            uv_max=uv_max,
            tint_color=tint_color,
        )

    def add_line_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_line_series

        Adds a line series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_line_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
        )

    def add_pie_series(
        self, *,
        x: float,
        y: float,
        radius: float,
        values: PLOT_DATA_TYPE,
        labels: t.List[str],
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        format: str = '%0.2f',
        angle: float = 90.0,
        normalize: bool = False,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_pie_series

        Adds a pie series to a plot.

        Args:
            x:
              ...
            y:
              ...
            radius:
              ...
            values:
              ...
            labels:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            format:
              ...
            angle:
              ...
            normalize:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_pie_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            radius=radius,
            values=values,
            labels=labels,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            format=format,
            angle=angle,
            normalize=normalize,
        )

    def add_plot_annotation(
        self, *,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        default_value: t.Any = (0.0, 0.0),
        offset: t.List[float] = (0.0, 0.0),
        color: t.List[int] = (0, 0, 0, -255),
        clamped: bool = True,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_plot_annotation

        Adds an annotation to a plot.

        Args:
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            default_value:
              ...
            offset:
              ...
            color:
              ...
            clamped:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_plot_annotation(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            default_value=default_value,
            offset=offset,
            color=color,
            clamped=clamped,
        )

    def add_scatter_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_scatter_series

        Adds a scatter series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_scatter_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
        )

    def add_shade_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y1: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y2: t.Any = [],
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_shade_series

        Adds a shade series to a plot.

        Args:
            x:
              ...
            y1:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            y2:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_shade_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y1=y1,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            y2=y2,
        )

    def add_stair_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_stair_series

        Adds a stair series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_stair_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
        )

    def add_stem_series(
        self, *,
        x: PLOT_DATA_TYPE,
        y: PLOT_DATA_TYPE,
        label: str = None,
        indent: int = -1,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_stem_series

        Adds a stem series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            indent:
              Offsets the widget to the right the specified number
              multiplied by the indent style.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_stem_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            indent=indent,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
        )

    def add_subplots(
        self, *,
        rows: int,
        columns: int,
        label: str = None,
        width: int = 0,
        height: int = 0,
        indent: int = -1,
        before: t.Optional[Widget] = None,
        callback: t.Optional[Callback] = None,
        show: bool = True,
        pos: t.List[int] = [],
        filter_key: str = '',
        delay_search: str = False,
        tracked: bool = False,
        track_offset: float = 0.5,
        user_data: t.Any = None,
        row_ratios: t.List[float] = [],
        column_ratios: t.List[float] = [],
        no_title: bool = False,
        no_menus: bool = False,
        no_resize: bool = False,
        no_align: bool = False,
        link_rows: bool = False,
        link_columns: bool = False,
        link_all_x: bool = False,
        link_all_y: bool = False,
        column_major: bool = False,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_subplots

        Adds a plot which is used to hold series, and can be drawn to with
        draw commands.

        Args:
            rows:
              ...
            columns:
              ...
            label:
              Overrides 'name' as label.
            width:
              Width of the item.
            height:
              Height of the item.
            indent:
              Offsets the widget to the right the specified number
              multiplied by the indent style.
            before:
              This item will be displayed before the specified item in the
              parent.
            callback:
              Registers a callback.
            show:
              Attempt to render widget.
            pos:
              Places the item relative to window coordinates, [0,0] is top
              left.
            filter_key:
              Used by filter widget.
            delay_search:
              Delays searching container for specified items until the end
              of the app. Possible optimization when a container has many
              children that are not accessed often.
            tracked:
              Scroll tracking
            track_offset:
              0.0f
            user_data:
              User data for callbacks.
            row_ratios:
              ...
            column_ratios:
              ...
            no_title:
              ...
            no_menus:
              the user will not be able to open context menus with right-
              click
            no_resize:
              resize splitters between subplot cells will be not be
              provided
            no_align:
              subplot edges will not be aligned vertically or horizontally
            link_rows:
              link the y-axis limits of all plots in each row (does not
              apply auxiliary y-axes)
            link_columns:
              link the x-axis limits of all plots in each column
            link_all_x:
              link the x-axis limits in every plot in the subplot
            link_all_y:
              link the y-axis limits in every plot in the subplot (does
              not apply to auxiliary y-axes)
            column_major:
              subplots are added in column major order instead of the
              default row major order
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_subplots(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            rows=rows,
            columns=columns,
            label=label,
            width=width,
            height=height,
            indent=indent,
            before=0 if before is None else before.dpg_id,
            callback=None if callback is None else callback.fn,
            show=show,
            pos=pos,
            filter_key=filter_key,
            delay_search=delay_search,
            tracked=tracked,
            track_offset=track_offset,
            user_data=user_data,
            row_ratios=row_ratios,
            column_ratios=column_ratios,
            no_title=no_title,
            no_menus=no_menus,
            no_resize=no_resize,
            no_align=no_align,
            link_rows=link_rows,
            link_columns=link_columns,
            link_all_x=link_all_x,
            link_all_y=link_all_y,
            column_major=column_major,
        )

    def add_text_point(
        self, *,
        x: float,
        y: float,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        x_offset: int = Ellipsis,
        y_offset: int = Ellipsis,
        vertical: bool = False,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_text_point

        Adds a labels series to a plot.

        Args:
            x:
              ...
            y:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            x_offset:
              ...
            y_offset:
              ...
            vertical:
              ...
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_text_point(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            y=y,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
            x_offset=x_offset,
            y_offset=y_offset,
            vertical=vertical,
        )

    def add_vline_series(
        self, *,
        x: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y_axis_dim: int = 1,
    ):
        """
        Refer:
        >>> dpg.add_vline_series

        Adds a infinite vertical line series to a plot.

        Args:
            x:
              ...
            label:
              Overrides 'name' as label.
            before:
              This item will be displayed before the specified item in the
              parent.
            source:
              Overrides 'id' as value storage key.
            show:
              Attempt to render widget.
            user_data:
              User data for callbacks.
            y_axis_dim:
              ...

        Returns:

        """

        _dpg_id = dpg.add_vline_series(
            parent=self.get_y_axis(axis_dim=y_axis_dim).dpg_id,
            x=x,
            label=label,
            before=0 if before is None else before.dpg_id,
            source=0 if source is None else source.dpg_id,
            show=show,
            user_data=user_data,
        )
