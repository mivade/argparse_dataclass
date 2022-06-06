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
