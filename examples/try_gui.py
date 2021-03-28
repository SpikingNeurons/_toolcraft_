import dataclasses
import numpy as np

from toolcraft import gui


@dataclasses.dataclass(frozen=True)
class Topic1(gui.CollapsingHeader):

    label: str = "Topic 1 - Text"

    message: gui.Text = gui.Text(
        msgs=[
            "This is topic 1. We will just add some bullet points ..."
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
class Topic2(gui.CollapsingHeader):

    label: str = "Topic 2 - Plots"

    message: gui.Text = gui.Text(
        msgs=[
            "This is topic 2. We will just add some plots ..."
        ],
    )
    line_plot: gui.Plot = gui.Plot(
        items=[
            gui.LineSeries(
                name="line 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            ),
            gui.LineSeries(
                name="line 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            )
        ],
        height=200,
    )
    scatter_plot: gui.Plot = gui.Plot(
        items=[
            gui.ScatterSeries(
                name="scatter 1",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            ),
            gui.ScatterSeries(
                name="scatter 2",
                x=np.arange(100),
                y=np.random.normal(0.0, scale=2.0, size=100)
            )
        ],
        height=200,
    )
    subplot: gui.ManagedColumn = gui.ManagedColumn(
        items=[
            gui.Plot(
                items=[
                    gui.LineSeries(
                        name="line 1",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    ),
                    gui.LineSeries(
                        name="line 2",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    )
                ],
                height=200,
            ),
            gui.Plot(
                items=[
                    gui.LineSeries(
                        name="line 1",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    ),
                    gui.LineSeries(
                        name="line 2",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    )
                ],
                height=200,
            ),
            gui.Plot(
                items=[
                    gui.LineSeries(
                        name="line 1",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    ),
                    gui.LineSeries(
                        name="line 2",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    )
                ],
                height=200,
            ),
            gui.Plot(
                items=[
                    gui.LineSeries(
                        name="line 1",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    ),
                    gui.LineSeries(
                        name="line 2",
                        x=np.arange(100),
                        y=np.random.normal(0.0, scale=2.0, size=100)
                    )
                ],
                height=200,
            ),
        ],
        columns=2,
        border=True,
    )


@dataclasses.dataclass(frozen=True)
class MyDashboard(gui.Dashboard):

    welcome_msg: gui.Text = gui.Text(
        msgs=[
            "Welcome to my dashboard",
            " ..... toolcraft ..... "
        ],
    )

    topic1: Topic1 = Topic1()
    topic2: Topic2 = Topic2()


def basic_dashboard():
    dash = MyDashboard(name="my_dashboard", label=" My Dashboard")
    dash.make_gui()
    dash.run_gui()


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



