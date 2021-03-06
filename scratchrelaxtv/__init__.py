# -*- coding: utf-8 -*-
"""scratchrelaxtv module.

scratchrelaxtv (anagram of extract-hcl-vars) is a Terraform module development
tool. Use it to:
* extract vars from HCL and generate an HCL variables file;
* generate a module-use stub file;
* delete files generated by scratchrelaxtv; and
* check whether existing files include all the variables used.

Example:
    Help using the scratchrelaxtv CLI can be found by typing the following::

        $ scratchrelaxtv --help
"""

import logging
import logging.config
import os
import re


__version__ = "0.6.17"
EXIT_OKAY = 0
EXIT_NOT_OKAY = 1

logging.config.fileConfig(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
logger = logging.getLogger(__name__)        # pylint: disable=invalid-name


def remove_prefix(text, prefix):
    """Remove prefix from a string."""
    return text[text.startswith(prefix) and len(prefix):]


def remove_files():
    """Remove files from the os that look like scratchrelaxtv files."""
    logger.info("attempting removal of files")
    pattern = r'^(variables\.\d+|modstub(\.\d+|))\.tf$'
    for root, _, files in os.walk(os.getcwd()):
        for file in filter(lambda x: re.match(pattern, x), files):
            os.remove(os.path.join(root, file))
            logger.info("removed file: %s", os.path.join(root, file))


class BassExtractor():
    """
    A class that extracts variables from Terraform HCL files to make creating
    Terraform modules easier.
    """

    # valid var names:
    # "A name must start with a letter and may contain only letters,
    # digits, underscores, and dashes."
    var_regex = r'\bvar\.([a-zA-Z][a-zA-Z0-9_-]*)\b'
    variable_regex = r'\bvariable "([^"]+)"'

    def __init__(self, args):
        self.args = args
        self.tf_vars = []
        self.log_arguments()

    def log_arguments(self):
        """Log the attributes of this run."""
        logger.info("input file: %s", self.args.input)
        logger.info("output file: %s", self.args.output)

        if self.args.force:
            logger.info("forcing overwrite of output file")
        else:
            logger.info("not forcing overwrite of output file")

        if self.args.asc:
            logger.info("ordering output file ascending")
        elif self.args.desc:
            logger.info("ordering output file descending")
        else:
            logger.info("not ordering output file")

    def _find_non_existing_filename(self):
        index = 1
        while True:
            if self.args.force or not os.path.isfile(self.args.output):
                return
            filename, file_extension = os.path.splitext(self.args.output)
            pattern = re.compile(r'(.*)\.(\d+)')
            search = pattern.search(filename)
            if search:
                filename = search.group(1)
                index = int(search.group(2)) + 1
            self.args.output = ''.join([
                filename, '.', str(index), file_extension])
            index += 1

    @staticmethod
    def get_file_contents(filename):
        """Return contents of file as a string."""
        entire_file = ""
        with open(filename, "r") as file_handle:
            entire_file = file_handle.read()
        return entire_file

    @staticmethod
    def find_vars(haystack, regex):
        """Extract vars from .tf file."""

        var_pattern = re.compile(regex)
        tf_vars = var_pattern.findall(haystack)
        tf_vars = list(dict.fromkeys(tf_vars))

        return tf_vars

    def find_vars_in_file(self, regex):
        """Extract vars from .tf file."""

        self.tf_vars = BassExtractor.find_vars(
            BassExtractor.get_file_contents(self.args.input),
            regex)

        if self.args.asc:
            self.tf_vars.sort()
        elif self.args.desc:
            self.tf_vars.sort(reverse=True)


class VarExtractor(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files to make creating
    Terraform modules easier.
    """
    def __init__(self, args):
        """Instantiate"""
        logger.info("generating variables file")

        # defaults
        if not args.input:
            args.input = "main.tf"

        if not args.output:
            args.output = "variables.tf"

        super().__init__(args)

    def write_file(self):
        """Output vars to .tf file."""
        self._find_non_existing_filename()
        with open(self.args.output, "w", encoding='utf_8') as file_handle:
            for tf_var in self.tf_vars:
                file_handle.write('variable "')
                file_handle.write(remove_prefix(tf_var, "var."))
                file_handle.write('" {\n')
                file_handle.write('  description = ""\n')
                file_handle.write('  type        = string\n')
                file_handle.write('  default     = ""\n')
                file_handle.write('}\n\n')

    def extract(self):
        """Extract vars from .tf file."""
        self.find_vars_in_file(self.var_regex)
        self.write_file()

        return EXIT_OKAY


class StubMaker(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files and generates a
    module-use stub.
    """
    def __init__(self, args):
        """Instantiate"""
        logger.info("generating module usage stub")

        # defaults
        if not args.input:
            args.input = "variables.tf"

        if not args.output:
            args.output = "modstub.tf"

        if not args.modname:
            args.modname = os.path.basename(os.getcwd())

        super().__init__(args)

    def write_file(self):
        """Output vars to .tf file."""
        self._find_non_existing_filename()
        with open(self.args.output, "w", encoding='utf_8') as file_handle:
            file_handle.write('module ')
            file_handle.write("".join(['"', self.args.modname, '"']))
            file_handle.write(" {\n")
            file_handle.write('  source = ')
            file_handle.write("".join(['"', "../", self.args.modname, '"']))
            file_handle.write("\n\n")
            file_handle.write("  providers = {\n    aws = \"aws\"\n  }\n\n")
            for tf_var in self.tf_vars:
                file_handle.write("".join([
                    '  ',
                    tf_var,
                    " = \"${local.",
                    tf_var, "}\"\n"]))
            file_handle.write('}\n\n')

    def extract(self):
        """Extract vars from .tf file."""
        self.find_vars_in_file(self.variable_regex)
        self.write_file()

        return EXIT_OKAY


class EnvGenerator(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files and generates a
    .env file.
    """
    def __init__(self, args):
        """Instantiate"""
        if args.env:
            logger.info("generating .env file")
        elif args.tfvars:
            logger.info("generating .tfvars file")

        # defaults
        if not args.input:
            args.input = "main.tf"

        if not args.output and args.env:
            args.output = ".env"

        if not args.output and args.tfvars:
            args.output = "terraform.tfvars"

        super().__init__(args)

    def _write_env(self):
        """Output vars to .env file."""
        with open(self.args.output, "w", encoding='utf_8') as file_handle:
            file_handle.write('unset "${!TF_VAR_@}"\n')
            for tf_var in self.tf_vars:
                file_handle.write("".join([
                    'export TF_VAR_',
                    tf_var,
                    "=replace\n"]))

    def _write_tfvars(self):
        """Output vars to .tfvars file."""
        with open(self.args.output, "w", encoding='utf_8') as file_handle:
            for tf_var in self.tf_vars:
                file_handle.write("".join([
                    tf_var,
                    ' = "replace"\n']))

    def write_file(self):
        """Output vars to file."""
        self._find_non_existing_filename()
        if self.args.env:
            self._write_env()
        elif self.args.tfvars:
            self._write_tfvars()

    def extract(self):
        """Extract vars from .tf file."""
        self.find_vars_in_file(self.var_regex)
        self.write_file()

        return EXIT_OKAY


class Checker(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files and checks them.
    """
    def __init__(self, args):
        """Instantiate"""
        logger.info("checking for missing variables")

        # defaults
        if not args.input:
            args.input = "main.tf"

        if not args.output:
            args.output = "variables.tf"

        super().__init__(args)

    def write_file(self):
        """Output vars to .tf file."""
        with open(self.args.output, "a+", encoding='utf_8') as file_handle:
            for tf_var in self.tf_vars:
                file_handle.write('\n')
                file_handle.write('variable "')
                file_handle.write(tf_var)
                file_handle.write('" {\n')
                file_handle.write('  description = ""\n')
                file_handle.write('  type        = string\n')
                file_handle.write('  default     = ""\n')
                file_handle.write('}\n')

    def find_missing(self):
        """Find missing vars in .tf files."""
        main_vars = self.find_vars(
            self.get_file_contents(self.args.input),
            self.var_regex)

        var_vars = self.find_vars(
            self.get_file_contents(self.args.output),
            self.variable_regex)

        return {
            'main': list(set(main_vars) - set(var_vars)),
            'var': list(set(var_vars) - set(main_vars))
        }

    def extract(self):
        """Check for missing vars in .tf files."""
        missing = self.find_missing()

        if missing['main']:
            logger.warning(
                "input file %s is missing variables:\n%s",
                self.args.input,
                '\n'.join(missing['main'])
            )
            if self.args.force:
                self.tf_vars = missing['main']
                self.write_file()
        if missing['var']:
            logger.warning(
                "variable file %s has unused variables:\n%s",
                self.args.output,
                '\n'.join(missing['var'])
            )

        return EXIT_OKAY


class TemplateExtractor(BassExtractor):
    """
    A class that extracts variables from templates used with Terraform and
    creates HCL showing all template variables.
    """

    var_regex = r'(?<!\$)\${([a-zA-Z][a-zA-Z0-9_-]+)}'

    def __init__(self, args):
        """Instantiate"""
        logger.info("extracting template variables")

        # defaults
        if not args.input:
            args.input = "template.sh"

        if not args.output:
            args.output = "template_vars.tf"

        super().__init__(args)

    def write_file(self):
        """Output vars to .tf file."""
        self._find_non_existing_filename()

        with open(self.args.output, "w", encoding='utf_8') as file_handle:

            file_handle.write('locals {\n')
            file_handle.write('  templates_vars = {\n')
            for tf_var in self.tf_vars:
                file_handle.write("".join([
                    "    ",
                    tf_var,
                    " = ",
                    "\"replace\"\n"]))
            file_handle.write('  }\n}\n')

    def extract(self):
        """Extract vars from .tf file."""
        self.find_vars_in_file(self.var_regex)
        self.write_file()

        return EXIT_OKAY
