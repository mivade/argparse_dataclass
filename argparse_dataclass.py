"""
``argparse_dataclass``
======================

Declarative CLIs with ``argparse`` and ``dataclasses``.

Features
--------

Features marked with a ✓ are currently implemented; features marked with a ⊘
are not yet implemented.

- [✓] Boolean flags
- [✓] Integer, string, float, and other simple types as arguments
- [✓] Default values
- [✓] Arguments with a finite set of choices
- [✓] Positional arguments
- [⊘] Subcommands
- [⊘] Mutually exclusive groups

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

Enabling choices for an option:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     small_integer: int = field(metadata=dict(choices=[1, 2, 3]))
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args(["--small-integer", "3"]))
    Options(small_integer=3)

To include positional arguments, set ``positional=True`` in the field metadata:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     optional: int
    ...     required: int = field(metadata=dict(positional=True))
    ...
    >>> parser = ArgumentParser(Options, prog="cli")
    >>> print(parser.parse_args(["--optional", "1", "2"]))
    Options(optional=1, required=2)

License
-------

MIT License

Copyright (c) 2020 Michael V. DePalatis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import argparse
from dataclasses import is_dataclass, MISSING
from typing import TypeVar

__version__ = "0.1.dev3"

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
            positional = field.metadata.get("positional", False)

            if positional:
                args = (name.replace("_", "-"),)
            else:
                args = (f"--{name.replace('_', '-')}",)

            kwargs = {
                "type": field.type,
                "help": field.metadata.get("help", None),
            }

            if field.metadata.get("choices") is not None:
                kwargs["choices"] = field.metadata["choices"]

            if (field.default == field.default_factory == MISSING) and not positional:
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
