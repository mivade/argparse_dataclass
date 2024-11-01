from __future__ import annotations
import unittest
from argparse_dataclass import dataclass


@dataclass
class Opt:
    x: int = 42
    y: bool = False


class ArgParseTests(unittest.TestCase):
    def test_basic(self):
        params = Opt.parse_args([])
        self.assertEqual(42, params.x)
        self.assertEqual(False, params.y)
        params = Opt.parse_args(["--x=10", "--y"])
        self.assertEqual(10, params.x)
        self.assertEqual(True, params.y)


if __name__ == "__main__":
    unittest.main()
