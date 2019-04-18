![scratch relax tv](https://github.com/YakDriver/scratchrelaxtv/raw/master/assets/srt.gif "Extract HCL Vars")

Terraform developer tool to extract variables and create `variables.tf` files.


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

*scratchrelaxtv* includes help:

```console
$ scratchrelaxtv --help
usage: scratchrelaxtv [-h] [-i INPUT] [-o OUTPUT] [-f] [-m] [-n MODNAME]
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
  -a, --asc             sort output variables in ascending order
  -d, --desc            sort output variables in descending order
```
