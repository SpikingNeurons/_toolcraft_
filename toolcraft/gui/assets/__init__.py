import enum
import pathlib
from dearpygui import core as dpg

_ASSET_FOLDER = pathlib.Path(__file__).parent.resolve()


class Font(enum.Enum):
    RobotoRegular = enum.auto()

    @property
    def file(self) -> pathlib.Path:
        return _ASSET_FOLDER / "fonts" / f"{self.name}.ttf"

    def set(self, size: float = 13.0):
        dpg.add_additional_font(
            file=self.file.as_posix(),
            size=size
        )
