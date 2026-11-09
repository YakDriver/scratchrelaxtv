![scratch relax tv](https://github.com/YakDriver/scratchrelaxtv/raw/main/assets/srt.gif "Extract HCL Vars")

<p>
    <a href="./LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/YakDriver/scratchrelaxtv.svg" /></a>
    <a href="https://github.com/YakDriver/scratchrelaxtv/actions/workflows/ci.yml" alt="Build status">
        <img src="https://github.com/YakDriver/scratchrelaxtv/actions/workflows/ci.yml/badge.svg?branch=main" /></a>
    <a href="https://pypi.python.org/pypi/scratchrelaxtv" alt="Python versions">
        <img src="https://img.shields.io/pypi/pyversions/scratchrelaxtv.svg" /></a>
    <a href="https://pypi.python.org/pypi/scratchrelaxtv" alt="Version">
        <img src="https://img.shields.io/pypi/v/scratchrelaxtv.svg" /></a>
</p>

Terraform module development tool.

1. Extract the variables a module uses and generate a `variables.tf` file
1. Check that a module declares every variable it uses and uses every variable it declares, from the command line or as a [pre-commit](https://pre-commit.com) hook
1. Generate a module use stub from a module's variable declarations
1. Generate a .env or `.tfvars` file with the variables a module uses
1. Generate HCL with template variables corresponding to variables from a Terraform template
1. Delete extra *scratchrelaxtv* files

*scratchrelaxtv* reads every `*.tf` file in the current directory, so modules split across `main.tf`, `locals.tf`, and other files are handled as a whole. Use `-i` to read a single file instead. Comments are ignored, so a commented-out `var.x` doesn't count as a use.

# install

```
pipx install scratchrelaxtv
```

Or run it without installing, using [uv](https://docs.astral.sh/uv/):

```
uvx scratchrelaxtv --help
```

`pip install scratchrelaxtv` also works. *scratchrelaxtv* requires Python 3.11 or newer.

# pre-commit

Add *scratchrelaxtv* to `.pre-commit-config.yaml` to check every module that has changed `.tf` files:

```yaml
repos:
  - repo: https://github.com/YakDriver/scratchrelaxtv
    rev: 0.7.0
    hooks:
      - id: relaxtv-check   # report undeclared and unused variables
      # - id: relaxtv-fix   # also add declarations for undeclared variables
```

Both hooks fail when a module has an undeclared or unused variable. `relaxtv-fix` adds the missing declarations to the module's `variables.tf`, so the next run passes unless unused variables remain. Remove those yourself.

# tips

Once installed, you can run *scratchrelaxtv* by typing either `relaxtv` or `scratchrelaxtv`. You can also run it as `python -m scratchrelaxtv`.

By default, *scratchrelaxtv* only prints warnings. Add `-v` to log each step.

Find out more about Terraform workflows and using *scratchrelaxtv* [here](https://medium.com/@dirk.avery/terraform-secure-simple-sweet-development-workflow-d7188d33d9cf).

# workflows

Here are two example workflows using *scratchrelaxtv*.

**Original module development**:
1. Write `main.tf` with whatever variables you need
1. Run *scratchrelaxtv* to generate `variables.tf`
1. Fill in descriptions, defaults, etc. in `variables.tf`
1. Run `terraform fmt` to prettify everything

**Cleanup module**:
1. Run `relaxtv -c` in the module's directory to find undeclared and unused variables
1. Run `relaxtv -cf` to automatically add declarations for undeclared variables to `variables.tf`
1. Fill in descriptions, defaults, etc. in `variables.tf` for newly added vars
1. Run `terraform fmt` to prettify everything

# examples

## example: generate `variables.tf`

By default, *scratchrelaxtv* reads every `*.tf` file in the current directory and generates a `variables.tf` file. (Use `-i` to read a single file.) Variables are in order of first use, reading files in alphabetical order. You can sort the variables using the `-a` (ascending) and `-d` (descending) options. You can also `--force` to overwrite an existing `variables.tf` file. Otherwise, *scratchrelaxtv* will generate new `variables.tf` files with each run: `variables.1.tf`, `variables.2.tf` and so on.

Assume this `main.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  count  = var.create_bucket ? 1 : 0
  bucket = var.bucket
  region = var.region
}
```

Run *scratchrelaxtv*:
```console
$ relaxtv
```

The generated `variables.tf`:
```hcl
variable "create_bucket" {
  description = ""
  type        = any
}

variable "bucket" {
  description = ""
  type        = any
}

variable "region" {
  description = ""
  type        = any
}
```

## example: find and fix missing variables

Assume you already have a `main.tf` and a `variables.tf`. In this example, the `variables.tf` is missing the `region` variable. `relaxtv -c` reports undeclared and unused variables and exits with status 1 if it finds any. Add `-f` to also add declarations for the undeclared ones.

`main.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  bucket = var.bucket
  region = var.region
}
```

`variables.tf`:
```hcl
variable "bucket" {
  description = "The bucket where the stuff will be stored"
  type        = string
  default     = ""
}
```

Run *scratchrelaxtv* to automatically add any missing variables:

```console
$ relaxtv -cf
scratchrelaxtv: .: undeclared variables: region
scratchrelaxtv: .: added declarations to variables.tf
```

Now, the `variables.tf` looks like this:
```hcl
variable "bucket" {
  description = "The bucket where the stuff will be stored"
  type        = string
  default     = ""
}

variable "region" {
  description = ""
  type        = any
}
```

## example: generate a stub for using the module

By default, when generating a stub, *scratchrelaxtv* reads the variable declarations in every `*.tf` file in the current directory.

Assume this `variables.tf`:
```hcl
variable "id" {
  description = "The ID of the resource"
  type        = string
  default     = ""
}

variable "bucket" {
  description = "The bucket where the stuff will be stored"
  type        = string
  default     = ""
}

variable "region" {
  description = "The AWS region where the bucket lives"
  type        = string
  default     = ""
}
```

Run *scratchrelaxtv* with the module stub option:
```console
$ relaxtv -m
```

The generated `modstub.tf`:
```hcl
module "tests2" {
  source = "../tests2"

  id     = local.id
  bucket = local.bucket
  region = local.region
}
```

## example: generate a `.tfvars` file

By default, when generating a `.tfvars` file, *scratchrelaxtv* reads every `*.tf` file in the current directory.

Assume this `main.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  bucket = var.bucket
  region = var.region
}
```

Run *scratchrelaxtv* with the generate `.tfvars` and sort-ascending options:
```console
$ relaxtv -ta
```

The generated `terraform.tfvars` file:
```
bucket = "replace"
region = "replace"
```

## example: generate a `.tf` file from Terraform template

By default, when using template mode, *scratchrelaxtv* looks for `template.sh`. (Use the `-i` to specify a different input file.)

Assume this `template.sh`:
```bash
#!/bin/bash

build_os="${build_os}"
build_type="${build_type}"
```

Run *scratchrelaxtv* with the `--template` and sort-ascending options:
```console
$ relaxtv -a --template
```

The generated `template_vars.tf` file:
```hcl
locals {
  templates_vars = {
    build_os   = "replace"
    build_type = "replace"
  }
}
```

## example: generate a `.env` (dotenv) file

By default, when generating a `.env` file, *scratchrelaxtv* reads every `*.tf` file in the current directory. (Use `-i` to read a single file.)

Assume this `main.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  bucket = var.bucket
  region = var.region
}
```

Run *scratchrelaxtv* with the generate `.env` and sort-ascending options:
```console
$ relaxtv -ea
```

The generated `.env`:
```bash
unset "${!TF_VAR_@}"
export TF_VAR_bucket=replace
export TF_VAR_region=replace
```

## example: remove files

```console
$ relaxtv -r
```

*scratchrelaxtv* can also tidy up your directories by removing its own extra generated files. Presumably it will only remove files you no longer need but *be careful*. This chart shows examples of what would be deleted or not.

**NOTE**: *scratchrelaxtv* removes files in the current directory _and subdirectories_.

| Filename | Deleted? |
| -------- | ------ |
| variables.tf | no |
| modstub.tf | yes |
| modstub.1.tf | yes |
| variables.1.tf | yes |
| xyz.abc | no |
| variables.a.tf | no |
| variables.43.tf | yes |
| modstub | no |
| modstub..tf | no |

# help

*scratchrelaxtv* includes help:

```console
$ relaxtv -h
usage: scratchrelaxtv [-h] [-i INPUT] [-o OUTPUT] [-f] [-m] [-n MODNAME] [-r]
                      [-c] [-e] [-t] [--template] [-a | -d] [-v] [--version]
                      [PATH ...]

positional arguments:
  PATH                  with -c: module directories or .tf files to check; a
                        file means its directory (default: the current
                        directory)

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        file to read (default: all *.tf files in the current
                        directory; template.sh with --template)
  -o OUTPUT, --output OUTPUT
                        file to write to
  -f, --force           overwrite existing output file (with -c: add missing
                        declarations)
  -m, --modstub         generate module usage stub
  -n MODNAME, --modname MODNAME
                        name to use in module stub
  -r, --remove          remove all modstub.tf, variables.#.tf files
  -c, --check           report undeclared and unused variables and exit 1 if
                        any; with -f, also add missing declarations
  -e, --env             generate .env with Terraform vars
  -t, --tfvars          generate .tfvars with Terraform vars
  --template            generate .tf from Terraform template vars
  -a, --asc             sort output variables in ascending order
  -d, --desc            sort output variables in descending order
  -v, --verbose         log each step, not only warnings
  --version             show program's version number and exit
```
