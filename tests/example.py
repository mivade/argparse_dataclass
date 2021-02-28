#!/usr/bin/env python3

from argparse_dataclass import dataclass


@dataclass
class Opt:
    x: int = 42
    y: bool = False


def main():
    params = Opt.parse_args()
    print(params)


if __name__ == "__main__":
    main()
