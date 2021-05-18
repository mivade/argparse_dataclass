import argparse
import unittest
from dataclasses import dataclass
from argparse_dataclass import ArgumentParser


@dataclass
class Opt:
    x: int = 42
    y: bool = False


class ArgumentParserTests(unittest.TestCase):
    def test_basic(self):
        params = ArgumentParser(Opt).parse_args([])
        self.assertEqual(42, params.x)
        self.assertEqual(False, params.y)
        params = ArgumentParser(Opt).parse_args(["--x=10", "--y"])
        self.assertEqual(10, params.x)
        self.assertEqual(True, params.y)



if __name__ == "__main__":
    unittest.main()