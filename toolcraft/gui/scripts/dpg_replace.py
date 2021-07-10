import inspect
import pathlib
import textwrap
import dearpygui.dearpygui as dpg

_method = dpg.add_combo


_signature = inspect.signature(_method)
_is_wrapped = '__wrapped__' in dir(_method)
_output = pathlib.Path("out.py")


# make _docs_dict
_main_doc = []
_docs_dict = {}
_track = False
for _l in _method.__doc__.split("\n"):
    _l_strip = _l.strip()
    if _l_strip in ['Returns:', 'Yields:']:
        break
    if _l_strip == 'Args:':
        _track = True
        continue
    if _track:
        _k = _l_strip.replace("*", '').split(' ')[0]
        print(_l_strip)
        _v = _l_strip.split(':')[1].strip()
        if _v == '':
            _v = '...'
        _docs_dict[_k] = _v
    else:
        for _s in textwrap.wrap(_l_strip, 70):
            _main_doc.append(f"\t{_s}")

# header
_lines = [
    "import dearpygui.dearpygui as dpg",
    "import dataclasses",
    "import typing as t",
    "",
    "",
    "@dataclasses.dataclass(frozen=True)",
    "class ___(Widget):",
    '\t"""',
    "\tRefer:",
    f"\t>>> dpg.{_method.__name__}",
    "",
] + _main_doc + ['\t"""', ""]

# make fields
_callback_params = []
_all_params_to_consider = []
for _param in _signature.parameters.values():
    _param_name = _param.name
    if _param_name in ['id', 'parent', 'before', ]:
        continue
    _param_type = f"{_param.annotation}".replace(
        'typing', 't'
    ).replace(
        "<class '", ""
    ).replace(
        "'>", ""
    ).replace(
        "t.Callable", "Callback"
    )
    _all_params_to_consider.append(_param_name)
    if _param_type.find("Callback") != -1:
        _callback_params.append(_param_name)
    _param_value = _param.default
    if _param_name == "source":
        _param_type = "t.Optional[Widget]"
        _param_value = "None"
    _parm_str = f"\t{_param_name}: {_param_type}"
    # noinspection PyUnresolvedReferences,PyProtectedMember
    if _param_value != inspect._empty:
        if _param_value in ["", "$$DPG_PAYLOAD"]:
            _parm_str += f" = '{_param_value}'"
        elif _param_value == []:
            _parm_str += f" = dataclasses.field(default_factory=list)"
        else:
            _parm_str += f" = {_param_value}"

    for _s in textwrap.wrap(_docs_dict[_param_name], 70):
        _lines.append(f"\t# {_s}")
    _lines.append(_parm_str)
    _lines.append("")


# make property is_container
_lines += [
    "\t@property",
    "\tdef is_container(self) -> bool:",
    f"\t\treturn {_is_wrapped}"
]

# make method build()
_kwargs = []
for _param in _all_params_to_consider:
    _assign_str = f"\t\t\t{_param}=self.{_param},"
    if _param == "source":
        _assign_str = \
            f"\t\t\tsource=0 if self.source is None else self.source.dpg_id,"
    if _param in _callback_params:
        _assign_str = f"\t\t\t{_param}=self.{_param}_fn,"
    _kwargs.append(_assign_str)
_lines += [
    "",
    "\tdef build(self) -> int:",
    f"\t\t_ret = dpg.{'add_' if _is_wrapped else ''}{_method.__name__}(",
    f"\t\t\t**self.internal.dpg_kwargs,",
    *_kwargs,
    f"\t\t)",
    f"\t\t",
    f"\t\treturn _ret",
]

# add methods for callback params
for _cp in _callback_params:
    _lines += [
        "",
        f"\tdef {_cp}_fn(self, **kwargs):",
        f"\t\tif self.{_cp} is None:",
        f"\t\t\treturn None",
        f"\t\telse:",
        f"\t\t\treturn self.{_cp}.fn()",
    ]

# write to disk
_result = "\n".join(_lines + [""])
print(_result)
_output.write_text(_result)
