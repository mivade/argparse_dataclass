"""
``argparse_dataclass``
======================

Declarative CLIs with ``argparse`` and ``dataclasses``.

.. image:: https://github.com/mivade/argparse_dataclass/actions/workflows/main.yml/badge.svg
    :target: https://github.com/mivade/argparse_dataclass/actions
    :alt: GitHub Actions status
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
    >>> from typing import Literal
    >>> @dataclass
    ... class Options:
    ...     small_integer: Literal[1, 2, 3]
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

Configuring a flag to have a default value of True:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     verbose: bool = True
    ...     logging: bool = field(default=True, metadata=dict(args=["--logging-off"]))
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args([]))
    Options(verbose=True, logging=True)
    >>> print(parser.parse_args(["--no-verbose", "--logging-off"]))
    Options(verbose=False, logging=False)


Configuring a flag so it is required to set:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     logging: bool = field(metadata=dict(required=True))
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args(["--logging"]))
    Options(logging=True)
    >>> print(parser.parse_args(["--no-logging"]))
    Options(logging=False)

Parsing only the known arguments:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     name: str
    ...     logging: bool = False
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_known_args(["--name", "John", "--other-arg", "foo"]))
    (Options(name='John', logging=False), ['--other-arg', 'foo'])


Configuring a field with the Optional generic type:

.. code-block:: pycon

    >>> from dataclasses import dataclass, field
    >>> from typing import Optional
    >>> from argparse_dataclass import ArgumentParser
    >>> @dataclass
    ... class Options:
    ...     name: str
    ...     id: Optional[int] = None
    ...
    >>> parser = ArgumentParser(Options)
    >>> print(parser.parse_args(["--name", "John"]))
    Options(name='John', id=None)
    >>> print(parser.parse_args(["--name", "John", "--id", "1234"]))
    Options(name='John', id=1234)

Contributors
------------

* @adsharma
* @asasine
* @frank113
* @jayvdb
* @jcal-15
* @mivade
* @rafi-cohen

License
-------

MIT License

Copyright (c) 2019-2023 argparse_dataclass contributors

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
from argparse import BooleanOptionalAction
from typing import (
    TypeVar,
    Optional,
    Sequence,
    Type,
    Tuple,
    get_origin,
    Literal,
    get_args,
    Union,
    Any,
    Generic,
)
from dataclasses import (
    Field,
    is_dataclass,
    fields,
    MISSING,
    dataclass as real_dataclass,
)
from importlib.metadata import version

# In Python 3.10, we can use types.NoneType
NoneType = type(None)

OptionsType = TypeVar("OptionsType")
ArgsType = Optional[Sequence[str]]

__version__ = version("argparse_dataclass")


def parse_args(options_class: Type[OptionsType], args: ArgsType = None) -> OptionsType:
    """Parse arguments and return as the dataclass type."""
    parser = argparse.ArgumentParser()
    _add_dataclass_options(options_class, parser)
    kwargs = _get_kwargs(parser.parse_args(args))
    return options_class(**kwargs)


def parse_known_args(
    options_class: Type[OptionsType], args: ArgsType = None
) -> Tuple[OptionsType, list[str]]:
    """Parse known arguments and return tuple containing dataclass type
    and list of remaining arguments.
    """
    parser = argparse.ArgumentParser()
    _add_dataclass_options(options_class, parser)
    namespace, others = parser.parse_known_args(args=args)
    kwargs = _get_kwargs(namespace)
    return options_class(**kwargs), others


def _add_dataclass_options(
    options_class: Type[OptionsType], parser: argparse.ArgumentParser
) -> None:
    if not is_dataclass(options_class):
        raise TypeError("cls must be a dataclass")

    for field in fields(options_class):
        args = field.metadata.get("args", [f"--{_get_arg_name(field)}"])
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

        # Support Literal types as an alternative means of specifying choices.
        if get_origin(field.type) is Literal:
            # Prohibit a potential collision with the choices field
            if field.metadata.get("choices") is not None:
                raise ValueError(
                    f"Cannot infer type of items in field: {field.name}. "
                    "Literal type arguments should not be combined with choices in the metadata. "
                    "Remove the redundant choices field from the metadata."
                )

            # Get the types of the arguments of the Literal
            types = [type(arg) for arg in get_args(field.type)]

            # Make sure just a single type has been used
            if len(set(types)) > 1:
                raise ValueError(
                    f"Cannot infer type of items in field: {field.name}. "
                    "Literal type arguments should contain choices of a single type. "
                    f"Instead, {len(set(types))} types where found: "
                    + ", ".join([type_.__name__ for type_ in set(types)])
                    + "."
                )

            # Overwrite the type kwarg
            kwargs["type"] = types[0]
            # Use the literal arguments as choices
            kwargs["choices"] = get_args(field.type)

        if field.metadata.get("metavar") is not None:
            kwargs["metavar"] = field.metadata["metavar"]

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
                        "specifying the type explicitly using metadata['type']"
                    )

        if field.default == field.default_factory == MISSING and not positional:
            kwargs["required"] = True
        elif field.default is not MISSING:
            kwargs["default"] = field.default
        else:
            kwargs["default"] = MISSING

        if field.type is bool:
            _handle_bool_type(field, args, kwargs)
        elif get_origin(field.type) is Union:
            if field.metadata.get("type") is None:
                # Optional[X] is equivalent to Union[X, None].
                f_args = get_args(field.type)
                if len(f_args) == 2 and NoneType in f_args:
                    arg = next(a for a in f_args if a is not NoneType)
                    kwargs["type"] = arg
                else:
                    raise TypeError(
                        "For Union types other than 'Optional', a custom 'type' must be specified using "
                        "'metadata'."
                    )

        if "group" in field.metadata:
            _handle_argument_group(parser, field, args, kwargs)
        else:
            parser.add_argument(*args, **kwargs)


def _get_kwargs(namespace: argparse.Namespace) -> dict[str, Any]:
    """Converts a Namespace to a dictionary containing the items that
    to be used as keyword arguments to the Options class.
    """
    return {k: v for k, v in vars(namespace).items() if v != MISSING}


def _handle_bool_type(field: Field, args: list, kwargs: dict):
    """Handles configuring the parser argument for boolean types.

    Different field configurations:
        No default value specified: action='store_true'
        Default value set to True : action='store_true'
        Default value set to False: action='store_false'
            Add a 'no-' prefix to the name if no custom args specified.
        if 'required' is specified: action=BooleanOptionalAction
    """
    kwargs["action"] = "store_true"
    for key in ("type", "required"):
        kwargs.pop(key, None)
    if "default" in kwargs:
        if field.default is True:
            kwargs["action"] = "store_false"
            if "args" not in field.metadata:
                args[0] = f"--no-{_get_arg_name(field)}"
                kwargs["dest"] = field.name
    elif field.metadata.get("required") is True:
        kwargs["action"] = BooleanOptionalAction
        kwargs["required"] = True


def _handle_argument_group(
    parser: argparse.ArgumentParser, field: Field, args: list, kwargs: dict
) -> None:
    """Handles adding the argument to an argument group."""
    groups = {x.title: x for x in parser._action_groups}
    group = field.metadata.get("group")
    if isinstance(group, str):
        title = group
        description = None
    elif isinstance(group, dict):
        title = group.get("title")
        description = group.get("description")
    elif isinstance(group, Sequence):
        len_ = len(group)
        title = group[0] if len_ > 0 else None
        description = group[1] if len_ > 1 else None
    else:
        raise TypeError("'group' must be a group title, dictionary, or sequence")
    group = groups.get(title)
    if title is None or group is None:
        group = parser.add_argument_group(title, description)
    group.add_argument(*args, **kwargs)


def _get_arg_name(field: Field):
    if field.metadata.get("keep_underscores", False):
        return field.name
    return field.name.replace("_", "-")


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

    def parse_args(self, args: ArgsType = None, namespace=None) -> OptionsType:
        """Parse arguments and return as the dataclass type."""
        if namespace is not None:
            raise ValueError("supplying a namespace is not allowed")
        kwargs = _get_kwargs(super().parse_args(args))
        return self._options_type(**kwargs)

    def parse_known_args(
        self, args: ArgsType = None, namespace=None
    ) -> Tuple[OptionsType, list[str]]:
        """Parse known arguments and return tuple containing dataclass type
        and list of remaining arguments.
        """
        if namespace is not None:
            raise ValueError("supplying a namespace is not allowed")
        namespace, others = super().parse_known_args(args=args)
        kwargs = _get_kwargs(namespace)
        return self._options_type(**kwargs), others


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
