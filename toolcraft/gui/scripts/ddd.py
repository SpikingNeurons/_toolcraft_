


@dataclasses.dataclass(frozen=True)
class PlotItem(abc.ABC):
    """
    Note that this is not a Widget nor a m.HashableClass as this will represent
    data that we will plot and there is no need to serialize it.
    """
    # This basically behaves like guid but we keep it as label so that users
    # can even add spaces or special characters inside label
    # Note that unlike guid they will be displayed in plot.
    # Also may be we can directly get latex expressions here :)
    # So guid for PlotItem is not sensible
    label: str

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
class VLineSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_vline_series
    """

    x: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.0
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

    @staticmethod
    def generate_from_npy(
        data: t.List[np.ndarray],
        label: t.List[str],
    ) -> t.List["VLineSeries"]:
        # ---------------------------------------------- 01
        # validate length of lists
        if len(data) != len(label):
            e.code.NotAllowed(
                msgs=[
                    f"We expect same number of items in data and label"
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

            # validate
            if _data.ndim != 1:
                e.code.NotAllowed(
                    msgs=[
                        f"We expect data to be 1D for index {_index}"
                    ]
                )

            # create series
            _ret.append(
                VLineSeries(
                    label=_label, x=_data
                )
            )

        # ---------------------------------------------- 03
        # return
        return _ret


@dataclasses.dataclass(frozen=True)
class HLineSeries(PlotItem):
    """
    Refer to
    >>> dpg.add_hline_series
    """

    x: PLOT_DATA_TYPE
    color: Color = Color.DEFAULT
    weight: float = 1.0
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

    @staticmethod
    def generate_from_npy(
        data: t.List[np.ndarray],
        label: t.List[str],
    ) -> t.List["HLineSeries"]:
        # ---------------------------------------------- 01
        # validate length of lists
        if len(data) != len(label):
            e.code.NotAllowed(
                msgs=[
                    f"We expect same number of items in data and label"
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

            # validate
            if _data.ndim != 1:
                e.code.NotAllowed(
                    msgs=[
                        f"We expect data to be 1D for index {_index}"
                    ]
                )

            # create series
            _ret.append(
                HLineSeries(
                    label=_label, x=_data
                )
            )

        # ---------------------------------------------- 03
        # return
        return _ret


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
    marker: Marker = Marker.Circle
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
