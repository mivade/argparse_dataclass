import sys
import unittest
import datetime as dt
from dataclasses import dataclass, field

from typing import List

from argparse_dataclass import ArgumentParser


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


class ArgumentParserTests(unittest.TestCase):
    def test_basic(self):
        @dataclass
        class Opt:
            x: int = 42
            y: bool = False

        params = ArgumentParser(Opt).parse_args([])
        self.assertEqual(42, params.x)
        self.assertEqual(False, params.y)
        params = ArgumentParser(Opt).parse_args(["--x=10", "--y"])
        self.assertEqual(10, params.x)
        self.assertEqual(True, params.y)

    def test_basic_negative(self):
        class Opt:
            x: int = 42
            y: bool = False

        self.assertRaises(TypeError, ArgumentParser, Opt)

    def test_no_defaults(self):
        @dataclass
        class Args:
            num_of_foo: int
            name: str

        params = ArgumentParser(Args).parse_args(["--num-of-foo=10", "--name", "Sam"])
        self.assertEqual(10, params.num_of_foo)
        self.assertEqual("Sam", params.name)

    def test_no_defaults_negative(self):
        @dataclass
        class Args:
            num_of_foo: int
            name: str

        with NegativeTestHelper() as helper:
            ArgumentParser(Args).parse_args([])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

    def test_nargs(self):
        @dataclass
        class Args:
            name: str
            friends: List[str] = field(metadata=dict(nargs=2))

        args = ["--name", "Sam", "--friends", "pippin", "Frodo"]
        params = ArgumentParser(Args).parse_args(args)
        self.assertEqual("Sam", params.name)
        self.assertEqual(["pippin", "Frodo"], params.friends)

    def test_nargs_plus(self):
        @dataclass
        class Args:
            name: str
            friends: List[str] = field(metadata=dict(nargs="+"))

        args = ["--name", "Sam", "--friends", "pippin", "Frodo"]
        params = ArgumentParser(Args).parse_args(args)
        self.assertEqual("Sam", params.name)
        self.assertEqual(["pippin", "Frodo"], params.friends)

        args += ["Bilbo"]
        params = ArgumentParser(Args).parse_args(args)
        self.assertEqual("Sam", params.name)
        self.assertEqual(["pippin", "Frodo", "Bilbo"], params.friends)

    def test_nargs_negative(self):
        @dataclass
        class Args:
            name: str
            friends: list = field(metadata=dict(nargs=2))

        self.assertRaises(ValueError, ArgumentParser, Args)

    def test_positional(self):
        @dataclass
        class Options:
            x: int = field(metadata=dict(args=["-x", "--long-name"]))
            positional: str = field(metadata=dict(args=["positional"]))

        params = ArgumentParser(Options).parse_args(["-x", "0", "POS_VALUE"])
        self.assertEqual(params.x, 0)
        self.assertEqual(params.positional, "POS_VALUE")

    def test_choices(self):
        @dataclass
        class Options:
            small_integer: int = field(metadata=dict(choices=[1, 2, 3]))

        params = ArgumentParser(Options).parse_args(["--small-integer", "2"])
        self.assertEqual(params.small_integer, 2)

    def test_choices_negative(self):
        @dataclass
        class Options:
            small_integer: int = field(metadata=dict(choices=[1, 2, 3]))

        with NegativeTestHelper() as helper:
            ArgumentParser(Options).parse_args(["--small-integer", "20"])
        self.assertIsNotNone(helper.exit_status, "Expected an error while parsing")

    def test_type(self):
        @dataclass
        class Options:
            name: str = field(metadata=dict(type=str.title))

        params = ArgumentParser(Options).parse_args(["--name", "john doe"])
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
        params = ArgumentParser(Parameters).parse_args([])
        e_time = dt.datetime.now()
        self.assertGreaterEqual(params.cutoff_date, s_time)
        self.assertLessEqual(params.cutoff_date, e_time)

        s_time = dt.datetime.now()
        params = ArgumentParser(Parameters).parse_args([])
        e_time = dt.datetime.now()
        self.assertGreaterEqual(params.cutoff_date, s_time)
        self.assertLessEqual(params.cutoff_date, e_time)

        date = dt.datetime(2000, 1, 1)
        params = ArgumentParser(Parameters).parse_args(
            ["--cutoff-date", date.isoformat()]
        )
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

        params = ArgumentParser(Parameters).parse_args([])
        self.assertEqual(params.message, "Default Message: 1")
        self.assertEqual(factory_calls, 1)

        params = ArgumentParser(Parameters).parse_args(["--message", "User message"])
        self.assertEqual(params.message, "User message")
        self.assertEqual(factory_calls, 1)

        params = ArgumentParser(Parameters).parse_args([])
        self.assertEqual(params.message, "Default Message: 2")
        self.assertEqual(factory_calls, 2)


if __name__ == "__main__":
    unittest.main()
