# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""test_scratchrelaxtv module."""


import os
from contextlib import contextmanager
from scratchrelaxtv import cli, VarExtractor, EXIT_OKAY


@contextmanager
def change_dir(path):
    """Change directory with context manager."""
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)


def test_parser():
    """Test CLI default arguments."""
    with change_dir("tests"):
        args = cli.parse_args([])
        assert args.input == "main.tf"
        assert args.output == "variables.tf"
        assert not args.force


def test_no_force():
    """Test extracting variables."""
    with change_dir("tests"):
        args = cli.parse_args([])

        filename = "variables.1.tf"

        assert not os.path.isfile(filename)
        extractor = VarExtractor(args)
        assert extractor.extract() == EXIT_OKAY
        assert os.path.isfile(filename)
        os.remove(filename)


def test_same_content():
    """Test extracting variables."""
    with change_dir("tests"):
        filename = "variables.1.tf"
        if os.path.isfile(filename):
            os.remove(filename)

        args = cli.parse_args(["-fa", "-o", filename])

        extractor = VarExtractor(args)

        assert extractor.extract() == EXIT_OKAY
        with open("variables.tf", "r", encoding='utf_8') as file_handle:
            first_list = file_handle.read().splitlines()
        with open("variables.1.tf", "r", encoding='utf_8') as file_handle:
            second_list = file_handle.read().splitlines()
        assert first_list == second_list
        os.remove(filename)
