import sys
import unittest
from dataclasses import dataclass
from argparse_dataclass import parse_args


class NegativeTestHelper:
    ''' Helper to enable testing of negative test cases. 
        On error parse_args() will call sys.exit(). 
        this will hijack that call and log the status code.
    '''
    def __init__(self):
        self._sys_exit = None
        self.exit_status: int = None

    def _on_exit(self, status: int):
        self.exit_status = status

    def __enter__(self):
        self._sys_exit = sys.exit
        sys.exit = self._on_exit
        return self

    def __exit__(self, *args, **kargs):
        sys.exit = self._sys_exit


class ArgumentParserTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()