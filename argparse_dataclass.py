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
Using dataclass decorator

.. code-block:: pycon

    >>> from argparse_dataclass import dataclass
    >>> @dataclass
    ... class Options:
    ...     x: int = 42
    ...     y: bool = False
    ...
    >>> print(Options.parse_args(['--y']))
    Options(x=42, y=True)

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

Using a custom type converter:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     name: str = field(metadata=dict(type=str.title))
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args(["--name", "john doe"]))
    Options(name='John Doe')

License
-------

MIT License

Copyright (c) 2021 Michael V. DePalatis and contributors

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
import sys
import argparse
from contextlib import suppress
from dataclasses import is_dataclass, fields, MISSING, dataclass as real_dataclass
from typing import TypeVar, Generic, Type

if sys.version_info[1] >= 8:
    # get_args was added in Python 3.8
    from typing import get_args
else:

    def get_args(f: Type) -> tuple:
        return getattr(f, "__args__", tuple())


__version__ = "0.2.0"

OptionsType = TypeVar("OptionsType")


def parse_args(options_class: Type[OptionsType], *args, **kwargs) -> OptionsType:
    """Parse arguments and return as the dataclass type."""
    parser = argparse.ArgumentParser()
    _add_dataclass_options(options_class, parser)
    namespace = parser.parse_args(*args, **kwargs)
    return options_class(**vars(namespace))


def _add_dataclass_options(
    options_class: Type[OptionsType], parser: argparse.ArgumentParser
) -> None:
    if not is_dataclass(options_class):
        raise TypeError("cls must be a dataclass")

    for field in fields(options_class):
        args = field.metadata.get("args", [f"--{field.name.replace('_', '-')}"])
        positional = not args[0].startswith("-")
        kwargs = {
            "type": field.metadata.get("type", field.type),
            "help": field.metadata.get("help", None),
        }

        if field.metadata.get("args") and not positional:
            # We want to ensure that we store the argument based on the
            # name of the field and not whatever flag name was provided
            kwargs["dest"] = field.name

        if field.metadata.get("choices") is not None:
            kwargs["choices"] = field.metadata["choices"]

        if field.metadata.get("nargs") is not None:
            kwargs["nargs"] = field.metadata["nargs"]
            if field.metadata.get("type") is None:
                # When nargs is specified, field.type should be a list,
                # or something equivalent, like typing.List.
                # Using it would most likely result in an error, so if the user
                # did not specify the type of the elements within the list, we
                # try to infer it:
                try:
                    kwargs["type"] = get_args(field.type)[0]  # get_args returns a tuple
                except IndexError:
                    # get_args returned an empty tuple, type cannot be inferred
                    raise ValueError(
                        f"Cannot infer type of items in field: {field.name}. "
                        "Try using a parameterized type hint, or "
                        "specifying the type explicitly using "
                        "metadata['type']"
                    )

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

        parser.add_argument(*args, **kwargs)


class ArgumentParser(argparse.ArgumentParser, Generic[OptionsType]):
    """Command line argument parser that derives its options from a dataclass.

    Parameters
    ----------
    options_class
        The dataclass that defines the options.
    args, kwargs
        Passed along to :class:`argparse.ArgumentParser`.

    """

    def __init__(self, options_class: Type[OptionsType], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._options_type: Type[OptionsType] = options_class
        _add_dataclass_options(options_class, self)

    def parse_args(self, *args, **kwargs) -> OptionsType:
        """Parse arguments and return as the dataclass type."""
        namespace = super().parse_args(*args, **kwargs)
        return self._options_type(**vars(namespace))


def dataclass(
    cls=None,
    *,
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=False,
):
    def wrap(cls):
        cls = real_dataclass(
            cls,
            init=init,
            repr=repr,
            eq=eq,
            order=order,
            unsafe_hash=unsafe_hash,
            frozen=frozen,
        )
        cls.parse_args = staticmethod(ArgumentParser(cls).parse_args)
        return cls

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @dataclass without parens.
    return wrap(cls)
