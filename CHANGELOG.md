# CHANGE LOG

## 0.7.0 - 2026.10.29

* **Breaking:** Requires Python 3.11 or newer. Python 2 and Python 3.5-3.10 are no longer supported.
* Packaging moved to `pyproject.toml` (hatchling), replacing `setup.py`, `setup.cfg`, `requirements/`, `.bumpversion.cfg`, and `MANIFEST.in`.
* CI moved from Travis CI, Azure Pipelines, and Mergify to GitHub Actions: ruff + mypy, a pytest matrix on Linux/macOS/Windows across Python 3.11-3.15, and a build + `twine check`. Added CodeQL (Python + Actions) and grouped weekly Dependabot updates.
* Releases are now tag-triggered and publish to PyPI with Trusted Publishing (no stored token).
* Removing the pinned `pip`, `virtualenv`, `pytest`, `pylint`, and `flake8` dev requirements clears all 27 open Dependabot alerts.
* Added type hints, a `py.typed` marker, and `python -m scratchrelaxtv`.
* The CLI now accepts `--version` and prints an error message with a non-zero exit code instead of a traceback when a file operation fails.
* No change to generated output: `variables.tf`, `modstub.tf`, `.env`, `.tfvars`, and template files are byte-for-byte identical to 0.6.17.

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
