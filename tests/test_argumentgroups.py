from dataclasses import dataclass, field
import unittest
import argparse
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
