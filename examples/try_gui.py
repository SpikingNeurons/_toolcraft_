import dataclasses
import numpy as np
import typing as t
from dearpygui import core as dpg

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
            "This is sub plot with ManagedColumn ..."
        ],
    )

    subplot: gui.ManagedColumn = gui.ManagedColumn(
        columns=2,
        border=True,
    )

    def plot_some_examples(self):
        # ------------------------------------------------------- 01
        # _simple_plot
        ...

        # ------------------------------------------------------- 02
        # _line_plot
        _line_plot = self.line_plot
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
        )
        for _i in _line_plot_items:
            _line_plot.plot(plot_type=_i)

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
        for _i in _scatter_plot_items:
            _scatter_plot.plot(plot_type=_i)

        # ------------------------------------------------------- 04
        _subplot = self.subplot
        for i in range(4):
            _plot = gui.Plot(height=200)
            _subplot.add_child(
                name=f"plot_{i}", widget=_plot
            )
            _plot.plot(
                gui.LineSeries(
                    label="line 1",
                    x=np.arange(100),
                    y=np.random.normal(0.0, scale=2.0, size=100)
                )
            )
            _plot.plot(
                gui.LineSeries(
                    label="line 2",
                    x=np.arange(100),
                    y=np.random.normal(0.0, scale=2.0, size=100)
                )
            )


@dataclasses.dataclass(frozen=True)
class ButtonAction(gui.CollapsingHeader):

    label: str = "Topic 3 - Button with threaded action"

    button_window: gui.ChildWindow = gui.ChildWindow()

    display_window: gui.ChildWindow = gui.ChildWindow()

    def build_children(self):
        _columns = gui.ManagedColumn(columns=2)
        _columns.build(name="columns", parent=self)
        _columns.add_child(
            name="button_window", widget=self.button_window
        )
        _columns.add_child(
            name="display_window", widget=self.display_window
        )


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

    topic3: ButtonAction = ButtonAction()

    def build_children(self):
        self.theme_selector.build(
            name='theme_selector', parent=self
        )
        self.welcome_msg.build(
            name='welcome_msg', parent=self
        )
        self.topic2.build(
            name='topic2', parent=self
        )
        self.topic1.build(
            name='topic1', parent=self,
            before=self.topic2
        )
        self.topic3.build(
            name='topic3', parent=self
        )


def basic_dashboard():
    _dash = MyDashboard(dash_id="my_dashboard", title="My Dashboard")
    _dash.build()
    _dash.topic2.plot_some_examples()
    _dash.run()


def demo():
    from dearpygui import core as dpgc
    gui.demo.show_demo()
    # dpgc.start_dearpygui(primary_window="Dear PyGui Demo")
    dpgc.start_dearpygui()


def main():
    basic_dashboard()
    # demo()


if __name__ == '__main__':
    main()



