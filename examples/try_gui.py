import dataclasses

from toolcraft import gui
from toolcraft.gui import widget

from dearpygui import simple as dpgs
from dearpygui import core as dpgc


@dataclasses.dataclass(frozen=True)
class MyDashboard(gui.Dashboard):
    ...


def basic_dashboard():
    ...


def main():
    basic_dashboard()


def demo():
    gui.demo.show_demo()
    dpgc.start_dearpygui()


if __name__ == '__main__':
    # main()
    demo()



