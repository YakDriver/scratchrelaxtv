"""scratchrelaxtv command line interface (CLI).

scratchrelaxtv (anagram of extract-hcl-vars) is a Terraform development
convenience tool that extracts vars from HCL and generates an HCL variables
file with the extracted vars. The point is to make creating Terraform modules
easier.

Running scratchrelaxtv without any options reads a main.tf, extracts the vars
from that file, and generates a variables.tf file with those variables.

Options include:
    -i, -o  changing input/output file names
    -f      force overwriting the output file
    -a, -d  sort ascending, descending (omit to preserve original order)
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import scratchrelaxtv


def parse_args(args: Sequence[str] | None) -> argparse.Namespace:
    """Parse args list."""
    parser = argparse.ArgumentParser(prog="scratchrelaxtv")
    parser.add_argument("-i", "--input", help="file to extract vars from")
    parser.add_argument("-o", "--output", help="file to write extracted vars to")
    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="overwrite existing out file",
    )

    task = parser.add_mutually_exclusive_group()
    task.add_argument(
        "-m",
        "--modstub",
        default=False,
        action="store_true",
        help="generate module usage stub",
    )
    parser.add_argument("-n", "--modname", help="name to use in module stub")
    task.add_argument(
        "-r",
        "--remove",
        default=False,
        action="store_true",
        help="remove all modstub.tf, variables.#.tf files",
    )
    task.add_argument(
        "-c",
        "--check",
        default=False,
        action="store_true",
        help="check that all vars are listed",
    )
    task.add_argument(
        "-e",
        "--env",
        default=False,
        action="store_true",
        help="generate .env with Terraform vars",
    )
    task.add_argument(
        "-t",
        "--tfvars",
        default=False,
        action="store_true",
        help="generate .tfvars with Terraform vars",
    )
    task.add_argument(
        "--template",
        default=False,
        action="store_true",
        help="generate .tf from Terraform template vars",
    )

    sort_order = parser.add_mutually_exclusive_group()
    sort_order.add_argument(
        "-a",
        "--asc",
        action="store_true",
        help="sort output variables in ascending order",
    )
    sort_order.add_argument(
        "-d",
        "--desc",
        action="store_true",
        help="sort output variables in descending order",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {scratchrelaxtv.__version__}",
    )

    return parser.parse_args(args)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for scratchrelaxtv CLI."""
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.remove:
        scratchrelaxtv.remove_files()
        return scratchrelaxtv.EXIT_OKAY

    extractor: scratchrelaxtv.BassExtractor
    if args.modstub:
        extractor = scratchrelaxtv.StubMaker(args)
    elif args.check:
        extractor = scratchrelaxtv.Checker(args)
    elif args.env or args.tfvars:
        extractor = scratchrelaxtv.EnvGenerator(args)
    elif args.template:
        extractor = scratchrelaxtv.TemplateExtractor(args)
    else:
        extractor = scratchrelaxtv.VarExtractor(args)

    try:
        return extractor.extract()
    except OSError as exc:
        print(f"scratchrelaxtv: {exc}", file=sys.stderr)
        return scratchrelaxtv.EXIT_NOT_OKAY


if __name__ == "__main__":
    sys.exit(main())
