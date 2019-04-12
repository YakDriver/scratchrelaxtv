# -*- coding: utf-8 -*-
"""scratchrelaxtv cli."""
import sys

import argparse

import scratchrelaxtv

click.disable_unicode_literals_warning = True


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.version_option(version=scratchrelaxtv.__version__)
@click.option(
    '--app-name',
    '-a',
    'app_name',
    default=None,
    envvar='GB_APP_NAME',
    help="Name of the Python application."
)
@click.option(
    '--pkg-name',
    '-n',
    'pkg_name',
    default=None,
    envvar='GB_PKG_NAME',
    help="The package name for the application you are building."
)
@click.option(
    '--script',
    '-s',
    'script_path',
    default=None,
    envvar='GB_SCRIPT',
    help="Path to Python application script installed by "
    + "pip in the virtual env."
)
@click.option(
    '--src-dir',
    '-d',
    'src_dir',
    default=None,
    envvar='GB_SRC_DIR',
    help="Source directory for the package."
)
@click.option(
    '--pkg-dir',
    '-p',
    'pkg_dir',
    default=None,
    envvar='GB_PKG_DIR',
    help="Directory where setup.py for app lives "
    + "(not for scratchrelaxtv).")
@click.option(
    '--extra-data',
    '-e',
    'extra_data',
    default=None,
    envvar='GB_EXTRA_DATA',
    multiple=True,
    help="Any extra data to be included with the "
    + "standalone application. Can be used multiple times."
)
@click.option(
    '--extra-pkgs',
    'extra_pkgs',
    default=[],
    envvar='GB_EXTRA_PKGS',
    multiple=True,
    help="Any extra package(s) to be included with the "
    + "standalone application. Can be used multiple times."
)
@click.option(
    '--extra-modules',
    'extra_modules',
    default=[],
    envvar='GB_EXTRA_MODULES',
    multiple=True,
    help="Any extra module(s) to be included with the "
    + "standalone application. Can be used multiple times."
)
@click.option(
    '--work-dir',
    '-w',
    'work_dir',
    default=None,
    envvar='GB_WORK_DIR',
    help="Relative path for work directory."
)
@click.option(
    '--onedir',
    'onedir',
    default=False,
    envvar='GB_ONEDIR',
    is_flag=True,
    help="Instead of packaging into one file, package in one directory."
)
@click.option(
    '--clean',
    '-c',
    'clean',
    default=False,
    envvar='GB_CLEAN',
    is_flag=True,
    help="Whether or not to clean up work area. If used, "
    + "the create standalone application will be placed in "
    + "the directory where scratchrelaxtv is run. Otherwise, "
    + "it is placed in the work_dir."
)
@click.option(
    '--name-format',
    '-f',
    'name_format',
    default=None,
    envvar='GB_NAME_FORMAT',
    help="Format to be used in naming the standalone "
    + "application. Can include {an}, {v}, {os}, {m} "
    + "for app name, version, os, and machine type "
    + "respectively."
)
@click.option(
    '--sha-format',
    'sha_format',
    default=None,
    envvar='GB_SHA_FORMAT',
    help="Format to be used in naming the SHA hash "
    + "file. Can include {an}, {v}, {os}, {m} "
    + "for app name, version, os, and machine type "
    + "respectively."
)
@click.option(
    '--label-format',
    'label_format',
    default=None,
    envvar='GB_LABEL_FORMAT',
    help="Format to be used in labeling generated files "
    + "in `scratchrelaxtv-files.json`. "
    + "Can include {An}, "
    + "{an}, {v}, {os}, {m}, and {ft} "
    + "for capitalized application "
    + "name, lowercase app name, version, OS, "
    + "machine, and file type ('Standalone "
    + "Executable' or "
    + "'Standalone Executable SHA256 Hash') "
    + "respectively. On Windows, .exe "
    + "will be added automatically. "
    + "Default: {An} {v} {ft} for {os} [scratchrelaxtv Build]"
)
@click.option(
    '--no-file',
    'no_file',
    default=False,
    envvar='GB_NO_FILE',
    is_flag=True,
    help="Do not write scratchrelaxtv-files.json file with "
    + "name of standalone."
)
@click.option(
    '--sha',
    'sha',
    default=scratchrelaxtv.Arguments.OPTION_SHA_INFO,
    envvar='GB_SHA',
    type=click.Choice([
        scratchrelaxtv.Arguments.OPTION_SHA_FILE,
        scratchrelaxtv.Arguments.OPTION_SHA_INFO
    ]),
    help="Where to put SHA256 hash for generated file."
)
@click.option(
    '--staging-dir',
    'staging_dir',
    default=None,
    envvar='GB_STAGING_DIR',
    help="Where to stage the artifacts of the build."
)
@click.option(
    '--with-latest',
    'with_latest',
    default=False,
    envvar='GB_WITH_LATEST',
    is_flag=True,
    help="Whether to include a latest directory as part of staging."
)
def main(**kwargs):
    """Entry point for scratchrelaxtv CLI."""
    print("scratchrelaxtv CLI,", scratchrelaxtv.__version__)

    # Create an instance
    sys.exit(scratchrelaxtv.ExtractVars(**kwargs))
