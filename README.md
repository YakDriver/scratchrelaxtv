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

1. Extract variables from `main.tf` and create `variables.tf` files
1. Create a module use stub from a `variables.tf` file
1. Delete extra *scratchrelaxtv* files


## simply

```
pip install scratchrelaxtv
```

In a directory with a `main.tf` file, run *scratchrelaxtv*:

```console
$ ls
main.tf
$ scratchrelaxtv
$ ls
main.tf			variables.tf
```

## details

### variables.tf

By default, it looks for `main.tf` and will keep variables in the resulting `variables.tf` in the order found in the `main.tf`. If variables are included more than once, they will only be listed once in the resulting `variables.tf`. If you do not `--force` overwriting, *scratchrelaxtv* will create new `variables.tf` files with each run: `variables.1.tf`, `variables.2.tf` and so on.

### modstub.tf

*scratchrelaxtv* can also be used to generate a module usage stub. By default, it looks for `variables.tf` and will keep variables in the resulting `modstub.tf` in the order found in the `variables.tf`. If variables are included more than once, they will only be listed once in the resulting `modstub.tf`. If you do not `--force` overwriting, *scratchrelaxtv* will create new `modstub.tf` files with each run: `modstub.1.tf`, `modstub.2.tf` and so on.

### remove files

*scratchrelaxtv* can also tidy up your directories by removing its own extra generated files. Presumably it will only remove files you no longer need but be careful. This chart shows examples of what would be deleted or not.

*scratchrelaxtv* removes files in the current directory _and subdirectories_.

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

### help

*scratchrelaxtv* includes help:

```console
$ scratchrelaxtv --help
usage: scratchrelaxtv [-h] [-i INPUT] [-o OUTPUT] [-f] [-m] [-n MODNAME] [-r]
                      [-a | -d]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        file to extract vars from
  -o OUTPUT, --output OUTPUT
                        file to write extracted vars to
  -f, --force           overwrite existing out file
  -m, --modstub         create module usage stub
  -n MODNAME, --modname MODNAME
                        name to use in module stub
  -r, --remove          remove all modstub.tf and variables.x.tf files
  -a, --asc             sort output variables in ascending order
  -d, --desc            sort output variables in descending order
```
