# -*- coding: utf-8 -*-
"""scratchrelaxtv command line interface (CLI).

scratchrelaxtv (anagram of extract-hcl-vars) is a Terraform development
convenience tool that extracts vars from HCL and creates an HCL variables file
with the extracted vars. The point is to make creating Terraform modules
easier.

Running scratchrelaxtv without any options reads a main.tf, extracts the vars
from that file, and creates a variables.tf file with those variables.

Options include:
    -i, -o  changing input/output file names
    -f      force overwriting the output file
    -a, -d  sort ascending, descending (omit to preserve original order)
"""
import argparse
import sys

import scratchrelaxtv


def parse_args(args):
    """Parse args list."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="file to extract vars from")
    parser.add_argument("-o", "--output",
                        help="file to write extracted vars to")
    parser.add_argument("-f", "--force", default=False, action="store_true",
                        help="overwrite existing out file")
    parser.add_argument("-m", "--modstub", default=False, action="store_true",
                        help="create module usage stub")
    parser.add_argument("-n", "--modname", help="name to use in module stub")
    parser.add_argument("-r", "--remove", default=False, action="store_true",
                        help="remove all modstub.tf and variables.x.tf files")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--asc", action="store_true",
                       help="sort output variables in ascending order")
    group.add_argument("-d", "--desc", action="store_true",
                       help="sort output variables in descending order")

    return parser.parse_args(args)


def main():
    """Entry point for scratchrelaxtv CLI."""
    args = parse_args(sys.argv[1:])

    extractor = None
    if args.remove:
        scratchrelaxtv.remove_files()
        sys.exit(scratchrelaxtv.EXIT_OKAY)
    elif not args.modstub:
        extractor = scratchrelaxtv.VarExtractor(args)
    else:
        extractor = scratchrelaxtv.StubMaker(args)
    sys.exit(extractor.extract())


if __name__ == "__main__":
    main()
