import enum
import typing as t
import dearpygui.dearpygui as dpg

from ... import error as e

_DPG_IDS_CACHE = {}


def extract_dpg_ids(
    enum_class: t.Type[enum.Enum], dpg_prefix: str
) -> t.Dict[enum.Enum, int]:
    # if there return
    if enum_class in _DPG_IDS_CACHE.keys():
        return _DPG_IDS_CACHE[enum_class]

    # get as not there in cache
    try:
        _ret = {}
        for k in dir(dpg):
            if k.startswith(dpg_prefix):
                _k = k.replace(dpg_prefix, "")
                if _k == "None":
                    _k = "NONE"
                _ret[enum_class[_k]] = getattr(dpg, k)
    except KeyError as ke:
        e.code.CodingError(
            msgs=[
                f"The enum class {enum_class} has no type {ke}"
            ]
        )
        raise

    # if empty _ret there is no dpg_prefix
    if not bool(_ret):
        e.code.CodingError(
            msgs=[
                f"Cannot find dpg ids in module {dpg} that start with prefix "
                f"{dpg_prefix}"
            ]
        )

    # check if there is any enum defined that is not provided by dpg
    for _enum in enum_class:
        if _enum not in _ret.keys():
            e.code.CodingError(
                msgs=[
                    f"There is no dpg id `{dpg_prefix}{_enum.name}` present "
                    f"in module {dpg}",
                    f"So please delete enum type {_enum.name} defined in class "
                    f"{enum_class}"
                ]
            )

    # save in cache
    _DPG_IDS_CACHE[enum_class] = _ret

    # return
    return _ret


from .core import *
from .plot import *
