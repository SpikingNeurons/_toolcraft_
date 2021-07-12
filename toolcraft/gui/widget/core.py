from ... import error as e
from .. import Widget, Callback, Color
from .auto import *


@dataclasses.dataclass(frozen=True)
class Table(BTable):
    # ...
    rows: int = None

    # ...
    columns: t.Union[int, t.List[str]] = None

    def init_validate(self):
        # call super
        super().init_validate()

        # check mandatory fields
        if self.rows is None:
            e.validation.NotAllowed(
                msgs=[
                    f"Please supply mandatory field `rows`"
                ]
            )
        if self.columns is None:
            e.validation.NotAllowed(
                msgs=[
                    f"Please supply mandatory field `columns`"
                ]
            )

    def init(self):
        # call super
        super().init()

        # add columns
        _num_columns = None
        if isinstance(self.columns, int):
            for _ in range(self.columns):
                self.add_child(
                    guid=f"c{_}", widget=Column(),
                )
            _num_columns = self.columns
        elif isinstance(self.columns, list):
            for _ in self.columns:
                self.add_child(
                    guid=f"c{_}", widget=Column(label=_),
                )
            _num_columns = len(self.columns)
        else:
            e.validation.NotAllowed(
                msgs=[
                    f"unknown type for field columns: {type(self.columns)}"
                ]
            )
            raise

        # add rows
        for _ in range(self.rows):
            # make row
            _row = Row()
            self.add_child(
                guid=f"r{_}", widget=_row,
            )
            # add cells to row
            for _c in range(_num_columns):
                _row.add_child(
                    guid=f"{_c}", widget=Group()
                )

    def get_cell(self, row: int, column: int) -> "Group":
        # noinspection PyTypeChecker
        return self.children[f"r{row}"].children[f"{column}"]

    def get_column(self, column: int) -> Column:
        # noinspection PyTypeChecker
        return self.children[f"c{column}"]

    def get_row(self, row: int) -> Row:
        # noinspection PyTypeChecker
        return self.children[f"r{row}"]


# noinspection PyDefaultArgument
@dataclasses.dataclass(frozen=True)
class Plot(BPlot):
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

    #
    width: int = -1

    #
    height: int = 400

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

    def clear(self):
        # plot series are added to YAxis so we clear its children to clear
        # the plot
        for _k, _w in self.children.items():
            if _k.startswith("_y"):
                dpg.delete_item(item=_w.dpg_id, children_only=True)

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
                    f"field `y{axis_dim}_axis` is not supplied while "
                    f"creating Plot instance"
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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

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
    ) -> int:
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
            int

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

        return _dpg_id

    def add_vline_series(
        self, *,
        x: PLOT_DATA_TYPE,
        label: str = None,
        before: t.Optional[Widget] = None,
        source: t.Optional[Widget] = None,
        show: bool = True,
        user_data: t.Any = None,
        y_axis_dim: int = 1,
    ) -> int:
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
            int

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

        return _dpg_id
