import argparse
import sys
import unittest
import datetime as dt
from dataclasses import dataclass, field

from typing import Optional, Union

from argparse_dataclass import add_dataclass_options, parse_args, parse_known_args


class NegativeTestHelper:
    """Helper to enable testing of negative test cases.
    On error parse_args() will call sys.exit().
    this will hijack that call and log the status code.
    """

    def __init__(self):
        self._sys_exit = None
        self.exit_status: int = None

    def _on_exit(self, status: int):
        self.exit_status = status
        raise RuntimeError("App Exited")

    def __enter__(self):
        self._sys_exit = sys.exit
        sys.exit = self._on_exit
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.exit = self._sys_exit
        return exc_type is RuntimeError and str(exc_value) == "App Exited"


class FunctionalParserTests(unittest.TestCase):
    def test_basic(self):
        @dataclass
        class Opt:
            x: int = 42
            y: bool = False

        params = parse_args(Opt, [])
        self.assertEqual(42, params.x)
        self.assertEqual(False, params.y)
        params = parse_args(Opt, ["--x=10", "--y"])
        self.assertEqual(10, params.x)
        self.assertEqual(True, params.y)

    def test_basic_negative(self):
        class Opt:
            x: int = 42
            y: bool = False

        self.assertRaises(TypeError, parse_args, Opt, [])

    def test_add_dataclass_options(self):
        @dataclass
        class Opt:
            x: int = 42
            y: bool = False
        argpument_parser = argparse.ArgumentParser()
        add_dataclass_options(Opt, argpument_parser)
        params = argpument_parser.parse_args([])
        print(params)
        self.assertEqual(42, params.x)
        self.assertEqual(False, params.y)
        params = argpument_parser.parse_args(["--x=10", "--y"])
        self.assertEqual(10, params.x)
        self.assertEqual(True, params.y)

    def test_bool_no_default(self):
        @dataclass
        class Opt:
            verbose: bool
            logging: bool

        params = parse_args(Opt, [])
        self.assertEqual(False, params.verbose)
        self.assertEqual(False, params.logging)
        params = parse_args(Opt, ["--verbose", "--logging"])
        self.assertEqual(True, params.verbose)
        self.assertEqual(True, params.logging)

    def test_bool_default_false(self):
        @dataclass
        class Opt:
            verbose: bool = False
            logging: bool = False

        params = parse_args(Opt, ["--verbose"])
        self.assertEqual(True, params.verbose)
        self.assertEqual(False, params.logging)
        with NegativeTestHelper() as helper:
            parse_args(Opt, ["--no-verbose"])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

    def test_bool_default_true(self):
        @dataclass
        class Opt:
            verbose: bool = True
            logging: bool = True

        params = parse_args(Opt, [])
        self.assertEqual(True, params.verbose)
        self.assertEqual(True, params.logging)
        params = parse_args(Opt, ["--no-verbose"])
        self.assertEqual(False, params.verbose)
        self.assertEqual(True, params.logging)

        with NegativeTestHelper() as helper:
            parse_args(Opt, ["--verbose"])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

    def test_bool_default_true_with_args(self):
        @dataclass
        class Opt:
            verbose: bool = field(default=True, metadata={"args": ["--silent"]})
            logging: bool = field(default=True, metadata={"args": ["--logging-off"]})

        params = parse_args(Opt, [])
        self.assertEqual(True, params.verbose)
        self.assertEqual(True, params.logging)
        params = parse_args(Opt, ["--silent"])
        self.assertEqual(False, params.verbose)
        self.assertEqual(True, params.logging)
        params = parse_args(Opt, ["--logging-off"])
        self.assertEqual(True, params.verbose)
        self.assertEqual(False, params.logging)
        params = parse_args(Opt, ["--silent", "--logging-off"])
        self.assertEqual(False, params.verbose)
        self.assertEqual(False, params.logging)

    def test_bool_required(self):
        @dataclass
        class Opt:
            verbose: bool = field(metadata={"required": True})
            logging: bool = field(
                metadata={"args": ["--enable-logging"], "required": True}
            )

        with NegativeTestHelper() as helper:
            parse_args(Opt, [])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")
        params = parse_args(Opt, ["--verbose", "--enable-logging"])
        self.assertEqual(True, params.verbose)
        self.assertEqual(True, params.logging)
        params = parse_args(Opt, ["--no-verbose", "--enable-logging"])
        self.assertEqual(False, params.verbose)
        self.assertEqual(True, params.logging)
        params = parse_args(Opt, ["--verbose", "--no-enable-logging"])
        self.assertEqual(True, params.verbose)
        self.assertEqual(False, params.logging)
        params = parse_args(Opt, ["--no-verbose", "--enable-logging"])
        self.assertEqual(False, params.verbose)
        self.assertEqual(True, params.logging)
        params = parse_args(Opt, ["--no-verbose", "--no-enable-logging"])
        self.assertEqual(False, params.verbose)
        self.assertEqual(False, params.logging)

    def test_no_defaults(self):
        @dataclass
        class Args:
            num_of_foo: int
            name: str

        params = parse_args(Args, ["--num-of-foo=10", "--name", "Sam"])
        self.assertEqual(10, params.num_of_foo)
        self.assertEqual("Sam", params.name)

    def test_no_defaults_negative(self):
        @dataclass
        class Args:
            num_of_foo: int
            name: str

        with NegativeTestHelper() as helper:
            parse_args(Args, [])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

    def test_nargs(self):
        @dataclass
        class Args:
            name: str
            friends: list[str] = field(metadata=dict(nargs=2))

        args = ["--name", "Sam", "--friends", "pippin", "Frodo"]
        params = parse_args(Args, args)
        self.assertEqual("Sam", params.name)
        self.assertEqual(["pippin", "Frodo"], params.friends)

    def test_nargs_plus(self):
        @dataclass
        class Args:
            name: str
            friends: list[str] = field(metadata=dict(nargs="+"))

        args = ["--name", "Sam", "--friends", "pippin", "Frodo"]
        params = parse_args(Args, args)
        self.assertEqual("Sam", params.name)
        self.assertEqual(["pippin", "Frodo"], params.friends)

        args += ["Bilbo"]
        params = parse_args(Args, args)
        self.assertEqual("Sam", params.name)
        self.assertEqual(["pippin", "Frodo", "Bilbo"], params.friends)

    def test_nargs_negative(self):
        @dataclass
        class Args:
            name: str
            friends: list = field(metadata=dict(nargs=2))

        args = ["--name", "Sam", "--friends", "pippin", "Frodo"]
        self.assertRaises(ValueError, parse_args, Args, args)

    def test_positional(self):
        @dataclass
        class Options:
            x: int = field(metadata=dict(args=["-x", "--long-name"]))
            positional: str = field(metadata=dict(args=["positional"]))

        params = parse_args(Options, ["-x", "0", "POS_VALUE"])
        self.assertEqual(params.x, 0)
        self.assertEqual(params.positional, "POS_VALUE")

    def test_choices(self):
        @dataclass
        class Options:
            small_integer: int = field(metadata=dict(choices=[1, 2, 3]))

        params = parse_args(Options, ["--small-integer", "2"])
        self.assertEqual(params.small_integer, 2)

    def test_choices_negative(self):
        @dataclass
        class Options:
            small_integer: int = field(metadata=dict(choices=[1, 2, 3]))

        with NegativeTestHelper() as helper:
            parse_args(Options, ["--small-integer", "20"])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

    def test_type(self):
        @dataclass
        class Options:
            name: str = field(metadata=dict(type=str.title))

        params = parse_args(Options, ["--name", "john doe"])
        self.assertEqual(params.name, "John Doe")

    @unittest.skipIf(
        sys.version_info[:2] == (3, 6),
        "Python 3.6 does not have datetime.fromisoformat()",
    )
    def test_default_factory(self):
        @dataclass
        class Parameters:
            cutoff_date: dt.datetime = field(
                default_factory=dt.datetime.now,
                metadata=dict(type=dt.datetime.fromisoformat),
            )

        s_time = dt.datetime.now()
        params = parse_args(Parameters, [])
        e_time = dt.datetime.now()
        self.assertGreaterEqual(params.cutoff_date, s_time)
        self.assertLessEqual(params.cutoff_date, e_time)

        s_time = dt.datetime.now()
        params = parse_args(Parameters, [])
        e_time = dt.datetime.now()
        self.assertGreaterEqual(params.cutoff_date, s_time)
        self.assertLessEqual(params.cutoff_date, e_time)

        date = dt.datetime(2000, 1, 1)
        params = parse_args(Parameters, ["--cutoff-date", date.isoformat()])
        self.assertEqual(params.cutoff_date, date)

    def test_default_factory_2(self):
        factory_calls = 0

        def factory_func():
            nonlocal factory_calls
            factory_calls += 1
            return f"Default Message: {factory_calls}"

        @dataclass
        class Parameters:
            message: str = field(default_factory=factory_func)

        params = parse_args(Parameters, [])
        self.assertEqual(params.message, "Default Message: 1")
        self.assertEqual(factory_calls, 1)

        params = parse_args(Parameters, ["--message", "User message"])
        self.assertEqual(params.message, "User message")
        self.assertEqual(factory_calls, 1)

        params = parse_args(Parameters, [])
        self.assertEqual(params.message, "Default Message: 2")
        self.assertEqual(factory_calls, 2)

    def test_parse_known_args(self):
        @dataclass
        class Options:
            name: str

        with NegativeTestHelper() as helper:
            parse_known_args(Options, [])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

        args = ["--name", "John Doe"]
        params, others = parse_known_args(Options, args)
        self.assertEqual(params.name, "John Doe")
        self.assertEqual(others, [])

        args = ["--name", "John Doe", "--cat", "hat"]
        params, others = parse_known_args(Options, args)
        self.assertEqual(params.name, "John Doe")
        self.assertEqual(others, ["--cat", "hat"])

    def test_optional_args(self):
        @dataclass
        class Options:
            name: str
            age: Optional[int] = None

        args = ["--name", "John Doe"]
        params = parse_args(Options, args)
        self.assertEqual(params.name, "John Doe")
        self.assertEqual(params.age, None)

        args = ["--name", "John Doe", "--age", "3"]
        params = parse_args(Options, args)
        self.assertEqual(params.name, "John Doe")
        self.assertEqual(params.age, 3)

    def test_optional_union_args(self):
        @dataclass
        class Options:
            name: str
            age: Union[None, int] = None

        args = ["--name", "John Doe"]
        params = parse_args(Options, args)
        self.assertEqual(params.name, "John Doe")
        self.assertEqual(params.age, None)

        args = ["--name", "John Doe", "--age", "3"]
        params = parse_args(Options, args)
        self.assertEqual(params.name, "John Doe")
        self.assertEqual(params.age, 3)


if __name__ == "__main__":
    unittest.main()
