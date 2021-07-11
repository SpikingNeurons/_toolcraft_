import dataclasses
import numpy as np
import time
import datetime
import typing as t
import dearpygui.dearpygui as dpg

from toolcraft import gui, util


@dataclasses.dataclass(frozen=True)
class Info(gui.CollapsingHeader):

    label: str = "Topic 1 - Text"

    message: gui.Text = gui.Text(
        msgs=[
            "This is topic 1. We will just add some bullet points below ..."
        ],
    )
    bullets: gui.Text = gui.Text(
        msgs=[
            "bullet 1",
            "bullet 2",
            "bullet 3",
            "bullet 4",
        ],
        bullet=True
    )


@dataclasses.dataclass(frozen=True)
class Plotting(gui.CollapsingHeader):

    label: str = "Topic 2 - Plotting"

    line_plot: gui.Plot = gui.Plot(
        label="This is line plot ...",
        height=200,
    )

    scatter_plot: gui.Plot = gui.Plot(
        label="This is scatter plot ...",
        height=200,
    )

    subplot_msg: gui.Text = gui.Text(
        msgs=[
            "This is sub plot with Group ..."
        ],
    )

    subplot: gui.Group = gui.Group()

    def plot_some_examples(self):
        # ------------------------------------------------------- 01
        # _simple_plot
        ...

        # ------------------------------------------------------- 02
        # _line_plot
        _line_plot = self.line_plot
        # noinspection PyTypeChecker
        _line_plot_items = [
            gui.LineSeries(
                label="line 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            ),
            gui.LineSeries(
                label="line 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            )
        ] + gui.LineSeries.generate_from_npy(
            data=[
                np.random.normal(0.0, scale=1.5, size=100)
                for _ in range(5)
            ],
            label=[f"line {i}" for i in range(3, 3+5)]
        ) + gui.VLineSeries.generate_from_npy(
            data=[
                np.asarray([1., 2.]), np.asarray([3., 4.])
            ],
            label=["vline1", "vline2"]
        ) + gui.HLineSeries.generate_from_npy(
            data=[
                np.asarray([1., 2.]), np.asarray([3., 4.])
            ],
            label=["hline1", "hline2"]
        )
        _line_plot.add_items(items=_line_plot_items)

        # ------------------------------------------------------- 03
        _scatter_plot = self.scatter_plot
        _scatter_plot_items = [
            gui.ScatterSeries(
                label="scatter 1",
                x=np.random.normal(1.0, scale=2.0, size=100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            ),
            gui.ScatterSeries(
                label="scatter 2",
                x=np.random.normal(0.0, scale=2.0, size=100),
                y=np.random.normal(1.0, scale=2.0, size=100),
            )
        ] + gui.ScatterSeries.generate_from_npy(
            data_x=np.random.normal(0.0, scale=1.5, size=500),
            data_y=np.random.normal(0.0, scale=1.5, size=500),
            label=np.random.randint(3, 3+5, 500),
            label_formatter="scatter {label}"
        )
        _scatter_plot.add_items(items=_scatter_plot_items)

        # ------------------------------------------------------- 04
        _subplot = self.subplot
        for i in range(4):
            _plot = gui.Plot(height=200)
            _subplot.add_child(
                guid=f"plot_{i}", widget=_plot
            )
            _plot.add_items(
                items=[
                    gui.LineSeries(
                        label="line 1",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    ),
                    gui.LineSeries(
                        label="line 2",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    ),
                ]
            )


@dataclasses.dataclass(frozen=True)
class ButtonPlotCallback(gui.Callback):

    receiver: gui.Widget

    def fn(self):
        # get sender
        # noinspection PyTypeChecker
        _sender = self.sender  # type: gui.Button

        # display to receiver i.e. add_child if not there
        if _sender.guid not in self.receiver.children.keys():

            # make collapsing header
            _collapsing_header = gui.CollapsingHeader(
                label=_sender.label, closable=False, default_open=True,
            )

            # add child to receiver
            self.receiver.add_child(
                guid=_sender.guid,
                widget=_collapsing_header
            )

            # make close button and add it collapsing header
            _close_button = gui.callback.CloseWidgetCallback.get_button_widget()
            _collapsing_header.add_child(
                guid="close_button", widget=_close_button
            )

            # make plot and add to collapsing header
            _plot = gui.Plot(
                label=f"This is plot for {_sender.label} ...",
                height=200,
            )
            _collapsing_header.add_child(
                guid="plot", widget=_plot
            )

            # add some data
            _plot.add_items(
                items=gui.LineSeries.generate_from_npy(
                    data=[
                        np.random.normal(0.0, scale=1.5, size=100)
                        for _ in range(5)
                    ],
                    label=[f"line {i}" for i in range(3, 3+5)]
                )
            )

        # else we do nothing as things are already plotted
        else:
            # in case user has close collapsable header we can attempt to
            # show it again
            # _collapsable_header = self.receiver.children[_sender.label]
            # _collapsable_header.show()
            ...


@dataclasses.dataclass(frozen=True)
class ButtonPlot(gui.CollapsingHeader):

    label: str = "Topic 3 - Button with threaded action"

    button_window: gui.Child = gui.Child()

    display_window: gui.Child = gui.Child()

    def layout(self):
        _columns = gui.Group()
        _columns.add_child(
            guid="button_window", widget=self.button_window
        )
        _columns.add_child(
            guid="display_window", widget=self.display_window
        )
        for i in range(5):
            self.button_window.add_child(
                guid=f"button{i}",
                widget=gui.Button(
                    width=300,
                    label=f"Button {i}",
                    callback=ButtonPlotCallback(
                        receiver=self.display_window
                    )
                ),
            )
        self.add_child(guid="columns", widget=_columns)


@dataclasses.dataclass(frozen=True)
class MyDashboard(gui.Dashboard):

    theme_selector: gui.Combo = gui.callback.SetThemeCallback.get_combo_widget()

    welcome_msg: gui.Text = gui.Text(
        msgs=[
            "Welcome to my dashboard",
            " ..... toolcraft ..... "
        ],
    )

    topic1: Info = Info()

    topic2: Plotting = Plotting()

    topic3: ButtonPlot = ButtonPlot()

    def layout(self):
        self.add_child(
            guid='theme_selector', widget=self.theme_selector
        )
        self.add_child(
            guid='welcome_msg', widget=self.welcome_msg
        )
        self.add_child(
            guid='topic2', widget=self.topic2
        )
        self.add_child(
            guid='topic1', widget=self.topic1, before=self.topic2
        )
        self.add_child(
            guid='topic3', widget=self.topic3
        )


def basic_dashboard():
    _dash = MyDashboard(dash_guid="my_dashboard", title="My Dashboard")
    _dash.build()
    # _dash.topic2.plot_some_examples()
    _dash.run()


def demo():
    gui.demo.show_demo()
    dpg.start_dearpygui()


def main():
    basic_dashboard()
    # demo()


if __name__ == '__main__':
    main()



