import typing as t
from dearpygui import core as dpg


def get_themes() -> t.List[str]:
    return [
        "Dark", "Light", "Classic", "Dark 2", "Grey", "Dark Grey", "Cherry",
        "Purple", "Gold", "Red"
    ]
