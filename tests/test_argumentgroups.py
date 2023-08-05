import argparse
from dataclasses import dataclass, field

import unittest

from argparse_dataclass import ArgumentParser


class ArgumentParserGroupsTests(unittest.TestCase):
    def test_basic_str(self):
        parser = argparse.ArgumentParser()
        group = parser.add_argument_group("title")
        group.add_argument("--x", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": "title"})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_basic_dict(self):
        title = "title"

        parser = argparse.ArgumentParser()
        group = parser.add_argument_group(title)
        group.add_argument("--x", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": {"title": title}})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_basic_dict_description(self):
        title = "title"
        description = "description"

        parser = argparse.ArgumentParser()
        group = parser.add_argument_group(title, description)
        group.add_argument("--x", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(
                metadata={"group": {"title": title, "description": description}}
            )

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_basic_sequence(self):
        parser = argparse.ArgumentParser()
        group = parser.add_argument_group("group")
        group.add_argument("--x", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": ("group")})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_basic_sequence_description(self):
        parser = argparse.ArgumentParser()
        group = parser.add_argument_group("group", "description")
        group.add_argument("--x", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": ("group", "description")})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_basic_empty(self):
        parser = argparse.ArgumentParser()
        group = parser.add_argument_group()
        group.add_argument("--x", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": ()})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_multiple_arguments(self):
        title = "title"

        parser = argparse.ArgumentParser()
        group = parser.add_argument_group(title)
        group.add_argument("--x", required=True, type=int)
        group.add_argument("--y", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": title})
            y: int = field(metadata={"group": title})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_multiple_groups_empty(self):
        parser = argparse.ArgumentParser()
        group_a = parser.add_argument_group()
        group_a.add_argument("--x", required=True, type=int)
        group_b = parser.add_argument_group()
        group_b.add_argument("--y", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            x: int = field(metadata={"group": ()})
            y: int = field(metadata={"group": ()})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)

    def test_argument_groups(self):
        title_a = "Group A"
        title_b = "Group B"
        descr_b = "Description B"
        title_c = "Group C"
        descr_c = "Description C"

        parser = argparse.ArgumentParser()
        group_a = parser.add_argument_group(title_a)
        group_a.add_argument("--arga1", required=True, type=int)
        group_a.add_argument("--arga2", required=True, type=int)
        group_b = parser.add_argument_group(title_b, descr_b)
        group_b.add_argument("--argb", required=True, type=int)
        group_c = parser.add_argument_group(title_c, descr_c)
        group_c.add_argument("--argc", required=True, type=int)
        group_d = parser.add_argument_group()
        group_d.add_argument("--argd", required=True, type=int)
        group_e = parser.add_argument_group()
        group_e.add_argument("--arge", required=True, type=int)
        group_a.add_argument("--arga3", required=True, type=int)
        expected = parser.format_help()

        @dataclass
        class Opt:
            arga1: int = field(metadata={"group": title_a})
            arga2: int = field(metadata={"group": title_a})
            argb: int = field(
                metadata={"group": {"title": title_b, "description": descr_b}}
            )
            argc: int = field(metadata={"group": (title_c, descr_c)})
            argd: int = field(metadata={"group": ()})
            arge: int = field(metadata={"group": ()})
            arga3: int = field(metadata={"group": title_a})

        parser = ArgumentParser(Opt)
        out = parser.format_help()

        self.assertEqual(expected, out)
