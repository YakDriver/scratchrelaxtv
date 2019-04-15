# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""test_scratchrelaxtv module."""


import os
import filecmp
from scratchrelaxtv import cli, VarExtractor, EXIT_OKAY


def test_parser():
    """Test CLI default arguments."""
    args = cli.parse_args([])
    assert args.input == "main.tf"
    assert args.output == "variables.tf"
    assert not args.force


def test_no_force():
    """Test extracting variables."""
    args = cli.parse_args([])

    filename = "variables.1.tf"

    assert not os.path.isfile(filename)
    extractor = VarExtractor(args)
    assert extractor.extract() == EXIT_OKAY
    assert os.path.isfile(filename)
    os.remove(filename)


def test_same_content():
    """Test extracting variables."""
    filename = "variables.1.tf"
    args = cli.parse_args(["-f", "-o", filename])

    extractor = VarExtractor(args)
    assert extractor.extract() == EXIT_OKAY
    assert filecmp.cmp("variables.tf", filename)
    os.remove(filename)
