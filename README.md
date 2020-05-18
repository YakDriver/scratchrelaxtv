![scratch relax tv](https://github.com/YakDriver/scratchrelaxtv/raw/master/assets/srt.gif "Extract HCL Vars")

<p>
    <a href="./LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/YakDriver/scratchrelaxtv.svg" /></a>
    <a href="http://travis-ci.org/YakDriver/scratchrelaxtv" alt="Build status">
        <img src="https://travis-ci.org/YakDriver/scratchrelaxtv.svg?branch=master" /></a>
    <a href="https://pypi.python.org/pypi/scratchrelaxtv" alt="Python versions">
        <img src="https://img.shields.io/pypi/pyversions/scratchrelaxtv.svg" /></a>
    <a href="https://pypi.python.org/pypi/scratchrelaxtv" alt="Version">
        <img src="https://img.shields.io/pypi/v/scratchrelaxtv.svg" /></a>
</p>

Terraform module development tool.

1. Extract variables from `main.tf` and generate a `variables.tf` file
1. Find missing variables in `variables.tf` and `main.tf` based on each other
1. Generate a module use stub from a `variables.tf` file
1. Generate a .env file with variables from `main.tf`
1. Delete extra *scratchrelaxtv* files

# install

```
pip install scratchrelaxtv
```

# tips

Once installed, you can run *scratchrelaxtv* by typing either `relaxtv` or `scratchrelaxtv`.

Find out more about Terraform workflows and using *scratchrelaxtv* [here](https://medium.com/@dirk.avery/terraform-secure-simple-sweet-development-workflow-d7188d33d9cf).

# workflows

Here are two example workflows using *scratchrelaxtv*.

**Original module development**:
1. Write `main.tf` with whatever variables you need
1. Run *scratchrelaxtv* to generate `variables.tf`
1. Fill in descriptions, defaults, etc. in `variables.tf`
1. Run `terraform fmt` to prettify everything

**Cleanup module**:
1. Run *scratchrelaxtv* in folder with `main.tf` and `variables.tf` to find missing variables
1. Using `-cf` option, automatically add missing vars to `variables.tf`
1. Fill in descriptions, defaults, etc. in `variables.tf` for newly added vars
1. Run `terraform fmt` to prettify everything

# examples

## example: generate `variables.tf`

By default, *scratchrelaxtv* looks for `main.tf` and will generate a `variables.tf` file. Variables will be in the same order in `variables.tf` as they were in `main.tf`. There are options to sort variables. You can `--force` to overwrite an existing `variables.tf` file. Otherwise, *scratchrelaxtv* will generate new `variables.tf` files with each run: `variables.1.tf`, `variables.2.tf` and so on.

Assume this `main.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  count  = "${var.create_bucket ? 1 : 0}"
  bucket = "${var.bucket}"
  region = "${var.region}"
}
```

Run *scratchrelaxtv*:
```console
$ relaxtv
2019-04-26 08:02:54,011 - INFO - generating variables file
2019-04-26 08:02:54,011 - INFO - input file: main.tf
2019-04-26 08:02:54,011 - INFO - output file: variables.tf
2019-04-26 08:02:54,011 - INFO - not forcing overwrite of output file
2019-04-26 08:02:54,011 - INFO - not ordering output file
```

The generated `variables.tf`:
```hcl
variable "create_bucket" {
  description = ""
  type        = string
  default     = ""
}

variable "bucket" {
  description = ""
  type        = string
  default     = ""
}

variable "region" {
  description = ""
  type        = string
  default     = ""
}
```

## example: find and fix missing variables

Assume you already have a `main.tf` and a `variables.tf`. In this example, the `variables.tf` is missing the `region` variable.

`main.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  bucket = "${var.bucket}"
  region = "${var.region}"
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
2019-04-26 08:21:27,289 - INFO - checking for missing variables
2019-04-26 08:21:27,289 - INFO - input file: main.tf
2019-04-26 08:21:27,289 - INFO - output file: variables.tf
2019-04-26 08:21:27,289 - INFO - forcing overwrite of output file
2019-04-26 08:21:27,289 - INFO - not ordering output file
2019-04-26 08:21:27,290 - WARNING - input file main.tf is missing variables:
region
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
  type        = string
  default     = ""
}
```

## example: generate a stub for using the module

By default, when generating a stub, *scratchrelaxtv* looks for `variables.tf`.

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
2019-04-26 08:09:27,147 - INFO - generating module usage stub
2019-04-26 08:09:27,147 - INFO - input file: variables.tf
2019-04-26 08:09:27,147 - INFO - output file: modstub.tf
2019-04-26 08:09:27,147 - INFO - not forcing overwrite of output file
2019-04-26 08:09:27,147 - INFO - not ordering output file
```

The generated `modstub.tf`:
```hcl
module "tests2" {
  source = "../tests2"

  providers = {
    aws = "aws"
  }

  id     = "${local.id}"
  bucket = "${local.bucket}"
  region = "${local.region}"
}
```

## example: generate a `.env` (dotenv) file

By default, when generating a `.env` file, *scratchrelaxtv* looks for `variables.tf`.

Assume this `variables.tf`:
```hcl
resource "aws_s3_bucket" "this" {
  bucket = "${var.bucket}"
  region = "${var.region}"
}
```

Run *scratchrelaxtv* with the generate `.env` and sort-ascending options:
```console
$ relaxtv -ea
2019-06-21 20:01:35,362 - INFO - generating .env file
2019-06-21 20:01:35,362 - INFO - input file: main.tf
2019-06-21 20:01:35,362 - INFO - output file: .env
2019-06-21 20:01:35,362 - INFO - not forcing overwrite of output file
2019-06-21 20:01:35,362 - INFO - ordering output file ascending
```

The generated `.env`:
```bash
unset "${!TF_VAR_@}"
TF_VAR_bucket=replace
TF_VAR_region=replace
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
$ relaxtv --help
usage: scratchrelaxtv [-h] [-i INPUT] [-o OUTPUT] [-f] [-m] [-n MODNAME] [-r]
                      [-c] [-e] [-a | -d]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        file to extract vars from
  -o OUTPUT, --output OUTPUT
                        file to write extracted vars to
  -f, --force           overwrite existing out file
  -m, --modstub         generate module usage stub
  -n MODNAME, --modname MODNAME
                        name to use in module stub
  -r, --remove          remove all modstub.tf, variables.#.tf files
  -c, --check           check that all vars are listed
  -e, --env             generate .env with Terraform vars
  -a, --asc             sort output variables in ascending order
  -d, --desc            sort output variables in descending order
```
