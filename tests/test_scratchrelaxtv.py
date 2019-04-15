# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""test_scratchrelaxtv module."""


import os
import filecmp
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
        assert extractor.extract() == EXIT_OKAY
        assert os.path.isfile(filename)
        os.remove(filename)


def test_same_content():
    """Test extracting variables."""
    with change_dir("tests"):
        filename = "variables.1.tf"
        args = cli.parse_args(["-f", "-o", filename])

        extractor = VarExtractor(args)
        assert extractor.extract() == EXIT_OKAY
        assert filecmp.cmp("variables.tf", filename)
        os.remove(filename)
