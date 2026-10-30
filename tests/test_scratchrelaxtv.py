"""Tests for the scratchrelaxtv library and CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from scratchrelaxtv import (
    EXIT_OKAY,
    Checker,
    EnvGenerator,
    StubMaker,
    TemplateExtractor,
    VarExtractor,
    __version__,
    cli,
    remove_files,
)


@contextmanager
def change_dir(path: str) -> Iterator[None]:
    """Change directory within a context, restoring the prior cwd on exit."""
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)


def test_var_defaults() -> None:
    """Test CLI default arguments."""
    with change_dir("tests"):
        args = cli.parse_args([])
        extractor = VarExtractor(args)
        assert extractor.args.input == "main.tf"
        assert extractor.args.output == "variables.tf"
        assert not extractor.args.force


def test_stub_defaults() -> None:
    """Test CLI default arguments."""
    with change_dir("tests"):
        args = cli.parse_args([])
        maker = StubMaker(args)
        assert maker.args.input == "variables.tf"
        assert maker.args.output == "modstub.tf"
        assert not maker.args.force


def test_no_force() -> None:
    """Test extracting variables."""
    with change_dir("tests"):
        args = cli.parse_args([])

        filename = "variables.1.tf"

        assert not os.path.isfile(filename)
        extractor = VarExtractor(args)
        assert extractor.extract() == EXIT_OKAY
        assert os.path.isfile(filename)
        os.remove(filename)


def test_same_content_vars() -> None:
    """Test extracting variables."""
    with change_dir("tests"):
        filename = "variables.1.tf"
        if os.path.isfile(filename):
            os.remove(filename)

        args = cli.parse_args(["-fa", "-o", filename])

        extractor = VarExtractor(args)

        assert extractor.extract() == EXIT_OKAY
        with open("variables.tf", encoding="utf-8") as file_handle:
            first_list = file_handle.read().splitlines()
        with open(filename, encoding="utf-8") as file_handle:
            second_list = file_handle.read().splitlines()
        assert first_list == second_list
        os.remove(filename)


def test_same_content_maker() -> None:
    """Test extracting variables."""
    with change_dir("tests"):
        filename = "modstub.1.tf"
        if os.path.isfile(filename):
            os.remove(filename)

        args = cli.parse_args(["-mfa", "-o", filename])

        maker = StubMaker(args)

        assert maker.extract() == EXIT_OKAY
        with open("modstub.tf", encoding="utf-8") as file_handle:
            first_list = file_handle.read().splitlines()
        with open(filename, encoding="utf-8") as file_handle:
            second_list = file_handle.read().splitlines()
        assert first_list == second_list
        os.remove(filename)


def test_removal() -> None:
    """Test removing files."""
    with change_dir("tests"):
        tmpdir = "tmpdir"
        os.mkdir(tmpdir)

        for name in ("modstub.tf", "variables.5.tf", "modstub.2.tf", "dont_delete.tf"):
            with open(os.path.join(tmpdir, name), "w", encoding="utf-8") as file_handle:
                file_handle.write("hello")

        with change_dir(tmpdir):
            remove_files()

        assert not os.path.isfile(os.path.join(tmpdir, "modstub.tf"))
        assert not os.path.isfile(os.path.join(tmpdir, "variables.5.tf"))
        assert not os.path.isfile(os.path.join(tmpdir, "modstub.2.tf"))
        assert os.path.isfile(os.path.join(tmpdir, "dont_delete.tf"))

        os.remove(os.path.join(tmpdir, "dont_delete.tf"))
        os.rmdir(tmpdir)


def test_check() -> None:
    """Test checking for missing variables."""
    with change_dir("tests"):
        args = cli.parse_args(["-c", "-i", "main_missing.tf", "-o", "variables_missing.tf"])

        checker = Checker(args)
        missing = checker.find_missing()

        assert len(missing["main"]) == 1
        assert missing["main"][0] == "create"
        assert len(missing["var"]) == 1
        assert missing["var"][0] == "extra_var"


def test_gen_env() -> None:
    """Test extracting variables."""
    with change_dir("tests"):
        filename = ".env.2"
        if os.path.isfile(filename):
            os.remove(filename)

        args = cli.parse_args(["-fea", "-o", filename])

        extractor = EnvGenerator(args)

        assert extractor.extract() == EXIT_OKAY
        with open(".env.1", encoding="utf-8") as file_handle:
            first_list = file_handle.read().splitlines()
        with open(filename, encoding="utf-8") as file_handle:
            second_list = file_handle.read().splitlines()
        assert first_list == second_list
        os.remove(filename)


def test_gen_tfvars() -> None:
    """Test extracting variables."""
    with change_dir("tests"):
        filename = "terraform.1.tfvars"
        if os.path.isfile(filename):
            os.remove(filename)

        args = cli.parse_args(["-fta", "-o", filename])

        extractor = EnvGenerator(args)

        assert extractor.extract() == EXIT_OKAY
        with open("terraform.tfvars", encoding="utf-8") as file_handle:
            first_list = file_handle.read().splitlines()
        with open(filename, encoding="utf-8") as file_handle:
            second_list = file_handle.read().splitlines()
        assert first_list == second_list
        os.remove(filename)


def test_template() -> None:
    """Test extracting variables."""
    with change_dir("tests"):
        filename = "template_vars.1.tf"
        if os.path.isfile(filename):
            os.remove(filename)

        args = cli.parse_args(["-fa", "--template", "-o", filename])

        extractor = TemplateExtractor(args)

        assert extractor.extract() == EXIT_OKAY
        with open("template_vars.tf", encoding="utf-8") as file_handle:
            first_list = file_handle.read().splitlines()
        with open(filename, encoding="utf-8") as file_handle:
            second_list = file_handle.read().splitlines()
        assert first_list == second_list
        os.remove(filename)


def test_remove_cli(tmp_path: Path) -> None:
    """The -r flag removes generated files and returns a clean exit code.

    Runs in an isolated temp directory so it never touches the committed
    fixtures under ``tests/``.
    """
    work = str(tmp_path)
    for name in ("modstub.tf", "variables.3.tf", "keep.tf"):
        with open(os.path.join(work, name), "w", encoding="utf-8") as file_handle:
            file_handle.write("x")

    with change_dir(work):
        assert cli.main(["-r"]) == EXIT_OKAY

    assert not os.path.isfile(os.path.join(work, "modstub.tf"))
    assert not os.path.isfile(os.path.join(work, "variables.3.tf"))
    assert os.path.isfile(os.path.join(work, "keep.tf"))


def test_remove_failure_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file that cannot be removed prints an error instead of a traceback."""
    (tmp_path / "modstub.tf").write_text("x", encoding="utf-8")

    def deny(path: str) -> None:
        raise PermissionError(13, "Permission denied", path)

    monkeypatch.setattr(os, "remove", deny)
    with change_dir(str(tmp_path)):
        assert cli.main(["-r"]) == 1
    assert "scratchrelaxtv:" in capsys.readouterr().err
    assert (tmp_path / "modstub.tf").exists()


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    """--version prints the package version and exits 0."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_missing_input_exits_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    """A missing input file prints an error and returns a non-zero code."""
    with change_dir("tests"):
        assert cli.main(["-i", "does_not_exist.tf", "-o", "variables.9.tf"]) == 1
        assert "scratchrelaxtv:" in capsys.readouterr().err


def test_python_dash_m() -> None:
    """The package is runnable via ``python -m scratchrelaxtv``."""
    result = subprocess.run(
        [sys.executable, "-m", "scratchrelaxtv", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
