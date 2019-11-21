"""
``argparse_dataclass``
======================

A simple module that allows for a more declarative approach to defining CLI
options.

Examples
--------

A simple parser with flags:

.. code-block:: pycon

    >>> from dataclasses import dataclass
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     verbose: bool
    ...     other_flag: bool
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args([]))
    Options(verbose=False, other_flag=False)
    >>> print(parser.parse_args(["--verbose", "--other-flag"]))
    Options(verbose=True, other_flag=True)

Using defaults:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     x: int = 1
    ...     y: int = field(default=2)
    ...     z: float = field(default_factory=lambda: 3.14)
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args([]))
    Options(x=1, y=2, z=3.14)

"""

import argparse
from dataclasses import is_dataclass, MISSING
from typing import TypeVar


OptionsType = TypeVar("OptionsType")


class ArgumentParser(argparse.ArgumentParser):
    """Command line argument parser that derives its options from a dataclass.

    Parameters
    ----------
    options_class
        The dataclass that defines the options.
    args, kwargs
        Passed along to :class:`argparse.ArgumentParser`.

    """

    def __init__(self, options_class: OptionsType, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._options_type: OptionsType = options_class
        self._add_dataclass_options()

    def _add_dataclass_options(self) -> None:
        if not is_dataclass(self._options_type):
            raise TypeError("cls must be a dataclass")

        for name, field in getattr(self._options_type, "__dataclass_fields__").items():
            args = (f"--{name.replace('_', '-')}",)
            kwargs = {
                "type": field.type,
                "help": field.metadata.get("help", None),
            }

            if field.default == field.default_factory == MISSING:
                kwargs["required"] = True
            else:
                if field.default_factory != MISSING:
                    kwargs["default"] = field.default_factory()
                else:
                    kwargs["default"] = field.default

            if field.type is bool:
                kwargs.pop("type")
                kwargs.pop("required")
                kwargs["action"] = "store_true"

            self.add_argument(*args, **kwargs)

    def parse_args(self, *args, **kwargs) -> OptionsType:
        """Parse arguments and return as the dataclass type."""
        namespace = super().parse_args(*args, **kwargs)
        return self._options_type(**vars(namespace))
