#!/usr/bin/env python3
from argparse_dataclass import dataclass
from typing import Literal


@dataclass
class Opt:
    x: int = 42
    y: bool = False
    z: Literal['a', 'b'] = 'a'


def main():
    params = Opt.parse_args()
    print(params)


if __name__ == "__main__":
    main()
