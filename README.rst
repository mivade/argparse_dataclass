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
