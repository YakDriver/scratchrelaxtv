"""Tests for multi-file scanning, comment handling, and the check hook."""

from __future__ import annotations

import contextlib
from pathlib import Path

import pytest

from scratchrelaxtv import EXIT_NOT_OKAY, EXIT_OKAY, cli, strip_comments


def write(directory: Path, **files: str) -> None:
    """Write files into directory; keyword ``main_tf`` becomes ``main.tf``."""
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (directory / name.replace("_tf", ".tf")).write_text(text, encoding="utf-8")


def run(directory: Path, *argv: str) -> int:
    """Run the CLI in directory."""
    with contextlib.chdir(directory):
        return cli.main(list(argv))


# Multi-file scanning


def test_generate_reads_all_tf_files(tmp_path: Path) -> None:
    write(
        tmp_path,
        main_tf='resource "x" "y" {\n  a = var.a\n}\n',
        locals_tf="locals {\n  b = var.b\n}\n",
    )
    assert run(tmp_path) == EXIT_OKAY
    text = (tmp_path / "variables.tf").read_text(encoding="utf-8")
    assert 'variable "a"' in text
    assert 'variable "b"' in text


def test_check_counts_declarations_in_any_file(tmp_path: Path) -> None:
    write(
        tmp_path,
        main_tf='variable "a" {}\n\noutput "a" {\n  value = var.a\n}\n',
    )
    assert run(tmp_path, "-c") == EXIT_OKAY


# Comments


@pytest.mark.parametrize(
    ("text", "expected_kept", "expected_removed"),
    [
        ("a = var.a # var.b\n", ["var.a"], ["var.b"]),
        ("a = var.a // var.b\n", ["var.a"], ["var.b"]),
        ("/* var.b\nvar.c */ a = var.a\n", ["var.a"], ["var.b", "var.c"]),
        ('url = "https://${var.host}/x" # var.b\n', ["var.host"], ["var.b"]),
        ('s = "a \\" # ${var.a}"\n', ["var.a"], []),
        (
            "u = <<-EOT\n  #!/bin/bash\n  echo ${var.a} # ${var.b}\n  EOT\n# var.c\n",
            ["var.a", "var.b"],
            ["var.c"],
        ),
    ],
)
def test_strip_comments(text: str, expected_kept: list[str], expected_removed: list[str]) -> None:
    result = strip_comments(text)
    for ref in expected_kept:
        assert ref in result
    for ref in expected_removed:
        assert ref not in result
    assert result.count("\n") == text.count("\n")


def test_commented_reference_is_not_a_use(tmp_path: Path) -> None:
    write(
        tmp_path,
        main_tf='# old = var.legacy\nresource "x" "y" {\n  a = var.a\n}\n',
        variables_tf='variable "a" {}\n',
    )
    assert run(tmp_path, "-c") == EXIT_OKAY


def test_commented_declaration_is_not_a_declaration(tmp_path: Path) -> None:
    write(
        tmp_path,
        main_tf='resource "x" "y" {\n  a = var.a\n}\n',
        variables_tf='# variable "a" {}\n',
    )
    assert run(tmp_path, "-c") == EXIT_NOT_OKAY


# Check exit status and output


def test_check_clean_is_silent(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path, main_tf='variable "a" {}\n\noutput "a" {\n  value = var.a\n}\n')
    assert run(tmp_path, "-c") == EXIT_OKAY
    assert capsys.readouterr() == ("", "")


def test_check_reports_undeclared_and_unused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(
        tmp_path,
        main_tf='resource "x" "y" {\n  a = var.a\n}\n',
        variables_tf='variable "old" {}\n',
    )
    assert run(tmp_path, "-c") == EXIT_NOT_OKAY
    err = capsys.readouterr().err
    assert "scratchrelaxtv: .: undeclared variables: a" in err
    assert "scratchrelaxtv: .: unused variables: old" in err


def test_fix_creates_variables_tf_then_passes(tmp_path: Path) -> None:
    write(tmp_path, main_tf='resource "x" "y" {\n  a = var.a\n  b = var.b\n}\n')
    assert run(tmp_path, "-cf") == EXIT_NOT_OKAY  # changed files
    assert (tmp_path / "variables.tf").read_text(encoding="utf-8") == (
        'variable "a" {\n  description = ""\n  type        = any\n}\n\n'
        'variable "b" {\n  description = ""\n  type        = any\n}\n'
    )
    assert run(tmp_path, "-cf") == EXIT_OKAY


def test_fix_appends_after_file_without_trailing_newline(tmp_path: Path) -> None:
    write(
        tmp_path,
        main_tf='resource "x" "y" {\n  a = var.a\n  b = var.b\n}\n',
        variables_tf='variable "a" {}',
    )
    assert run(tmp_path, "-cf") == EXIT_NOT_OKAY
    assert (
        (tmp_path / "variables.tf")
        .read_text(encoding="utf-8")
        .startswith('variable "a" {}\n\nvariable "b" {\n')
    )


# Paths (pre-commit passes changed file names)


def test_check_paths_checks_each_module(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path / "good", main_tf='variable "a" {}\n\noutput "a" {\n  value = var.a\n}\n')
    write(tmp_path / "bad", main_tf='output "a" {\n  value = var.a\n}\n')
    files = ["good/main.tf", "bad/main.tf", "good/main.tf"]
    assert run(tmp_path, "-c", *files) == EXIT_NOT_OKAY
    err = capsys.readouterr().err
    assert "bad: undeclared variables: a" in err
    assert "good" not in err


def test_check_paths_accepts_directories(tmp_path: Path) -> None:
    write(tmp_path / "m", main_tf='variable "a" {}\n\noutput "a" {\n  value = var.a\n}\n')
    assert run(tmp_path, "-c", "m") == EXIT_OKAY


@pytest.mark.parametrize("argv", [["x.tf"], ["-m", "x.tf"], ["-c", "-i", "main.tf", "x.tf"]])
def test_paths_rejected_outside_check(tmp_path: Path, argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        run(tmp_path, *argv)
    assert exc.value.code == 2


# Logging


def test_generate_is_quiet_by_default(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path, main_tf='resource "x" "y" {\n  a = var.a\n}\n')
    assert run(tmp_path) == EXIT_OKAY
    assert capsys.readouterr() == ("", "")


def test_verbose_logs_steps(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path, main_tf='resource "x" "y" {\n  a = var.a\n}\n')
    assert run(tmp_path, "-v") == EXIT_OKAY
    err = capsys.readouterr().err
    assert "INFO - generating variables file" in err
    assert "INFO - input files: main.tf" in err
