"""
The rule for now is to
+ have class members as UI widgets
+ have dataclass fields be specific to instance i.e. data etc.
"""
import abc
import dataclasses
import addict
import typing as t

from .. import error as e
from .. import logger
from .. import util

_LOGGER = logger.get_logger()


class _ReadOnlyClass(type):
    def __setattr__(self, key, value):
        e.code.NotAllowed(
            msgs=[
                f"Class {self} is read only.",
                f"You cannot override its attribute {key!r} programmatically.",
                f"Edit it during class definition ..."
            ]
        )


@dataclasses.dataclass(frozen=True)
class Builder(abc.ABC):

    class LITERAL(metaclass=_ReadOnlyClass):

        def __new__(cls, *args, **kwargs):
            e.code.NotAllowed(
                msgs=[
                    f"This class is meant to be used to hold class "
                    f"variables only",
                    f"Do not try to create instance of {cls} ..."
                ]
            )

    @property
    @abc.abstractmethod
    def id(self) -> str:
        ...

    @property
    @util.CacheResult
    def children(self) -> t.Dict[t.Union[int, str], "Widget"]:
        """
        children are those dataclass fields that are also instance of class
        `Widget`
        """
        # container
        _ret = {}

        # loop over
        for f in dataclasses.fields(self):
            # get value for each field
            v = getattr(self, f.name)

            # never have Dashboard as a child
            if isinstance(v, Dashboard):
                e.code.CodingError(
                    msgs=[
                        f"{Dashboard} is never meant to be used as "
                        f"a child. Avoid using it as dataclass field"
                    ]
                )

            # check if it is widget and make it children
            if isinstance(v, Widget):
                # append
                _ret[f.name] = v

            # rest all values are ignored ... you can use them as instance
            # values for any reason ... only widgets are tracked and laid out
            # in UI
            ...

        # return
        return _ret

    def __post_init__(self):

        self.init_validate()

        self.init()

    def init_validate(self):
        ...

    def init(self):
        ...

    def make_gui(self):
        ...


@dataclasses.dataclass(frozen=True)
class WidgetInternal:
    name: str
    parent: t.Union["Dashboard", "Widget"]

    @property
    def id(self) -> str:
        return f"{self.parent.id}.{self.name}"


@dataclasses.dataclass(frozen=True)
class Widget(Builder, abc.ABC):

    class LITERAL(Builder.LITERAL):
        internal = "internal"

    @property
    def id(self) -> str:
        return self.internal.id

    @property
    @util.CacheResult
    def internal(self) -> WidgetInternal:
        if self.LITERAL.internal in self.__dict__.keys():
            return self.__dict__[self.LITERAL.internal]
        else:
            e.code.CodingError(
                msgs=[
                    f"the method {self.set_internal} needs to be called before "
                    f"accessing property `internal`"
                ]
            )

    def init(self):

        # call super
        super().init()

        # every self will assign itself as parent for all its children i.e.
        # dataclass fields of this class which are instance of class Widget
        for k, c in self.children.items():
            c.set_internal(
                internal=WidgetInternal(name=k, parent=self)
            )

    def set_internal(self, internal: WidgetInternal):
        if self.LITERAL.internal in self.__dict__.keys():
            e.code.CodingError(
                msgs=[
                    f"internal was already set for widget {self}",
                    f"We expect the set_internal to be called only once during "
                    f"the lifetime of the program."
                ]
            )
        else:
            self.__dict__[self.LITERAL.internal] = internal


@dataclasses.dataclass(frozen=True)
class WidgetContainer(Widget, abc.ABC):

    items: t.List[Widget]

    @property
    @util.CacheResult
    def children(self) -> t.Dict[int, "Widget"]:
        # call parent implementation of children
        # we expect it to be empty
        _children = super().children
        if bool(_children):
            e.code.CodingError(
                msgs=[
                    f"Widgets can only be supplied as a list to `items` field",
                    f"Looks like that there are some dataclass fields which "
                    f"hold instance of class {Widget}"
                ]
            )

        # children here are elements in list
        return {
            f"item[{i}]": v for i, v in enumerate(self.items)
        }


@dataclasses.dataclass(frozen=True)
class Dashboard(Widget, abc.ABC):

    name: str

    @property
    def id(self) -> str:
        # for dashboard there is no parent so we have attribute name that
        # will be the id of super parent
        return self.name

