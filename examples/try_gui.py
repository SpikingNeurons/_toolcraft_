import dataclasses

from toolcraft import gui
from toolcraft.gui import widget

from dearpygui import simple as dpgs
from dearpygui import core as dpgc


@dataclasses.dataclass(frozen=True)
class Header1(widget.CollapsingHeader):
    name: str = "Header 1"
    label: str = "Header i Label"
    message: widget.Text = widget.Text(
        msgs=[
            "Welcome to my dashboard -- Header1",
            "Know more at ..."
        ],
    )


@dataclasses.dataclass(frozen=True)
class MyDashboard(gui.Dashboard):

    welcome_msg: widget.Text = widget.Text(
        msgs=[
            "Welcome to my dashboard",
            "Know more at ..."
        ],
    )

    header1: Header1 = Header1()


def basic_dashboard():
    dash = MyDashboard(name="my_dashboard", label=" My Dashboard")
    dash.make_gui()
    dash.run_gui()


def demo():
    gui.demo.show_demo()
    # dpgc.start_dearpygui(primary_window="Dear PyGui Demo")
    dpgc.start_dearpygui()


def main():
    basic_dashboard()
    # demo()


if __name__ == '__main__':
    main()



