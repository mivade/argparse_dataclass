"""
``argparse_dataclass``
======================

Declarative CLIs with ``argparse`` and ``dataclasses``.

.. image:: https://travis-ci.org/mivade/argparse_dataclass.svg?branch=master
    :target: https://travis-ci.org/mivade/argparse_dataclass

.. image:: https://img.shields.io/pypi/v/argparse_dataclass
    :alt: PyPI

Features
--------

Features marked with a ✓ are currently implemented; features marked with a ⊘
are not yet implemented.

- [✓] Positional arguments
- [✓] Boolean flags
- [✓] Integer, string, float, and other simple types as arguments
- [✓] Default values
- [✓] Arguments with a finite set of choices
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

Using different flag names and positional arguments:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     x: int = field(metadata=dict(args=["-x", "--long-name"]))
    ...     positional: str = field(metadata=dict(args=["positional"]))
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args(["-x", "0", "positional"]))
    Options(x=0, positional='positional')
    >>> print(parser.parse_args(["--long-name", 0, "positional"]))
    Options(x=0, positional='positional')

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
from contextlib import suppress
from dataclasses import is_dataclass, MISSING
from typing import TypeVar

__version__ = "0.1.0"

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
            args = field.metadata.get("args", [f"--{name.replace('_', '-')}"])
            positional = not args[0].startswith("-")
            kwargs = {
                "type": field.type,
                "help": field.metadata.get("help", None),
            }

            if field.metadata.get("args") and not positional:
                # We want to ensure that we store the argument based on the
                # name of the field and not whatever flag name was provided
                kwargs["dest"] = field.name

            if field.metadata.get("choices") is not None:
                kwargs["choices"] = field.metadata["choices"]

            if field.default == field.default_factory == MISSING and not positional:
                kwargs["required"] = True
            else:
                if field.default_factory != MISSING:
                    kwargs["default"] = field.default_factory()
                else:
                    kwargs["default"] = field.default

            if field.type is bool:
                kwargs["action"] = "store_true"

                for key in ("type", "required"):
                    with suppress(KeyError):
                        kwargs.pop(key)

            self.add_argument(*args, **kwargs)

    def parse_args(self, *args, **kwargs) -> OptionsType:
        """Parse arguments and return as the dataclass type."""
        namespace = super().parse_args(*args, **kwargs)
        return self._options_type(**vars(namespace))
