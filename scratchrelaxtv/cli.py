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
import contextlib
import copy
import errno
import logging
import os
import sys
from collections.abc import Sequence

import scratchrelaxtv


def parse_args(args: Sequence[str] | None) -> argparse.Namespace:
    """Parse args list."""
    parser = argparse.ArgumentParser(prog="scratchrelaxtv")
    parser.add_argument(
        "-i",
        "--input",
        help="file to read (default: all *.tf files in the current directory; "
        "template.sh with --template)",
    )
    parser.add_argument("-o", "--output", help="file to write to")
    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="overwrite existing output file (with -c: add missing declarations)",
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
        help="report undeclared and unused variables and exit 1 if any; "
        "with -f, also add missing declarations",
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
        "-v",
        "--verbose",
        action="store_true",
        help="log each step, not only warnings",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {scratchrelaxtv.__version__}",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help="with -c: module directories or .tf files to check; a file means its "
        "directory (default: the current directory)",
    )

    parsed = parser.parse_args(args)
    if parsed.paths and not parsed.check:
        parser.error("PATH arguments are only supported with -c")
    if parsed.paths and parsed.input:
        parser.error("-i cannot be combined with PATH arguments")
    return parsed


def _configure_logging(verbose: bool) -> None:
    """Send warnings (or, with -v, every step) to stderr."""
    handler = logging.StreamHandler(sys.stderr)
    if verbose:
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    else:
        handler.setFormatter(logging.Formatter("scratchrelaxtv: %(message)s"))
    logger = scratchrelaxtv.logger
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    logger.propagate = False


def _module_dirs(paths: list[str]) -> list[str]:
    """Return the unique module directories for paths, in sorted order.

    Raises FileNotFoundError for a path that doesn't exist, so a mistyped module
    path fails instead of checking (or, with -f, changing) another module.
    """
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
    dirs = {path if os.path.isdir(path) else os.path.dirname(path) or "." for path in paths}
    return sorted(dirs)


def _check(args: argparse.Namespace) -> int:
    """Check each module directory and return 1 if any has a problem."""
    if not args.paths:
        return scratchrelaxtv.Checker(args).extract()

    status = scratchrelaxtv.EXIT_OKAY
    for directory in _module_dirs(args.paths):
        with contextlib.chdir(directory):
            checker = scratchrelaxtv.Checker(copy.copy(args), label=directory)
            status = max(status, checker.extract())
    return status


def _run(args: argparse.Namespace) -> int:
    """Run the task selected by args and return its exit code."""
    if args.remove:
        scratchrelaxtv.remove_files()
        return scratchrelaxtv.EXIT_OKAY

    extractor: scratchrelaxtv.BassExtractor
    if args.modstub:
        extractor = scratchrelaxtv.StubMaker(args)
    elif args.check:
        return _check(args)
    elif args.env or args.tfvars:
        extractor = scratchrelaxtv.EnvGenerator(args)
    elif args.template:
        extractor = scratchrelaxtv.TemplateExtractor(args)
    else:
        extractor = scratchrelaxtv.VarExtractor(args)

    return extractor.extract()


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for scratchrelaxtv CLI."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    _configure_logging(args.verbose)

    try:
        return _run(args)
    except OSError as exc:
        print(f"scratchrelaxtv: {exc}", file=sys.stderr)
        return scratchrelaxtv.EXIT_NOT_OKAY


if __name__ == "__main__":
    sys.exit(main())
