# CHANGE LOG

## 0.7.0 - 2026.11.09

* **Breaking:** Requires Python 3.11 or newer. Python 2 and Python 3.5-3.10 are no longer supported.
* Packaging moved to `pyproject.toml` (hatchling), replacing `setup.py`, `setup.cfg`, `requirements/`, `.bumpversion.cfg`, and `MANIFEST.in`.
* CI moved from Travis CI, Azure Pipelines, and Mergify to GitHub Actions: ruff + mypy, a pytest matrix on Linux/macOS/Windows across Python 3.11-3.15, and a build + `twine check`. Added CodeQL (Python + Actions) and grouped weekly Dependabot updates.
* Releases are now tag-triggered and publish to PyPI with Trusted Publishing (no stored token).
* Removing the pinned `pip`, `virtualenv`, `pytest`, `pylint`, and `flake8` dev requirements clears all 27 open Dependabot alerts.
* Added type hints, a `py.typed` marker, and `python -m scratchrelaxtv`.
* The CLI now accepts `--version` and prints an error message with a non-zero exit code instead of a traceback when a file operation fails, including when `-r` cannot delete a file.
* **Breaking:** Generated variable declarations now use `type = any` and no `default`, so new variables are required until you choose a type and default. Previously every variable got `type = string` and `default = ""`, which was wrong for non-string inputs and made required inputs silently optional ([#250](https://github.com/YakDriver/scratchrelaxtv/issues/250)). This applies to `variables.tf` generation and to `-cf`.
* **Breaking:** The module stub (`-m`) uses HCL2 references (`bucket = local.bucket` instead of `bucket = "${local.bucket}"`) and no longer adds `providers = { aws = "aws" }`. Terraform warns that quoted references are deprecated and will be removed, and the block assumed the AWS provider ([#87](https://github.com/YakDriver/scratchrelaxtv/issues/87)).
* Generated `.tf` and `.tfvars` files are now aligned the way `terraform fmt` formats them, so `terraform fmt` makes no further changes.
* **Breaking:** By default, *scratchrelaxtv* reads every `*.tf` file in the current directory instead of only `main.tf` (or `variables.tf` for `-m`). Modules split across several files are now checked and generated correctly. `-i` still selects a single file. `-c` counts declarations in any file, not only `variables.tf`.
* **Breaking:** `-c` exits with status 1 when it finds undeclared or unused variables, so it can fail CI. With `-f`, it still exits 1 after adding declarations, so the change gets reviewed. Warnings now name the module directory.
* Add pre-commit hooks: `relaxtv-check` (`relaxtv -c`) and `relaxtv-fix` (`relaxtv -cf`). `-c` accepts module directories or `.tf` file paths and checks each module once.
* References are read only from HCL expressions, including `${...}` and `%{...}` in strings and heredocs. A `var.x` in a comment or in literal text such as `description = "Replaces var.x"` no longer counts, and declarations count only as top-level `variable` blocks.
* Output is quiet by default: only warnings are printed, to stderr. `-v` logs each step. Logging is configured by the CLI, not when the library is imported, and `logging.conf` is removed.
* A variable referenced only in its own `validation` block is reported as unused. References to other variables in a validation block still count.
* `-r` no longer descends into `.git`, `.terraform`, or `.terragrunt-cache`, so it can't delete files in downloaded modules.
* README shows `pipx install` and `uvx`.
* README examples now match actual output.

## 0.6.0 - 2020.05.29

* Output Terraform 0.12.x variables (variables without `"${}"`)
* Add feature to extract template variables from templates and generate corresponding HCL

## 0.5.2 - 2019.07.19

* Add compatibility with HCL2 / Terraform 0.12.x variables (variables without `"${}"`)
* Remove feature to automatically set lists default value to an empty list (does not work well with HCL2-style variables)

## 0.5.0 - 2019.07.02

* Add feature to generate Terraform variables (`.tfvars`) file

## 0.4.0 - 2019.06.21

* Add feature to generate dot-env (`.env`) file

## 0.3.0 - 2019.04.25

* Add functionality to check existing `main.tf` and `variables.tf` for missing variables

## 0.2.1 - 2019.04.25

* Fix inconsequential error thrown when removing files

## 0.2.0 - 2019.04.25

* Add capability to delete extra working files

## 0.1.3 - 2019.04.17

* Add module stub capability

## 0.1.2 - 2019.04.17

* Add simple docs

## 0.1.1 - 2019.04.16

* Initial working version

## 0.1.0 - 2019.04.15

* Initial release!
