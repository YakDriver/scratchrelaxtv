# -*- coding: utf-8 -*-
"""scratchrelaxtv module.

scratchrelaxtv (anagram of extract-hcl-vars) is a Terraform module development
tool. Use it to:
* extract vars from HCL and generate an HCL variables file;
* generate a module-use stub file;
* delete files created by scratchrelaxtv; and
* check whether existing files include all the variables used.

Example:
    Help using the scratchrelaxtv CLI can be found by typing the following::

        $ scratchrelaxtv --help
"""

import logging
import logging.config
import os
import re


__version__ = "0.3.0"
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
    main_phrase_find = r'(\[")?\$\{([^\}]*)\}("\])?'
    # valid var names:
    # "A name must start with a letter and may contain only letters,
    # digits, underscores, and dashes."
    main_token_find = r'\bvar\.([a-zA-Z][a-zA-Z0-9_-]*)\b'
    var_phrase_find = r'(\n)?variable "([^"]+)"'
    var_token_find = r'(.+)'

    def __init__(self, args):
        self.args = args
        self.tf_vars = []
        self.tf_lists = []
        self.log_arguments()

    def log_arguments(self):
        """Log all the attributes of this run."""
        if self.args.modstub:
            logger.info("creating module usage stub")
        elif self.args.remove:
            logger.info("attempting removal of files")
        elif self.args.check:
            logger.info("checking for missing variables")
        else:
            logger.info("creating variables.tf file")

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
    def find_vars(haystack, phrase, token):
        """Extract vars from .tf file."""

        interpol_pattern = re.compile(phrase)
        interpolations = interpol_pattern.findall(haystack)

        var_pattern = re.compile(token)
        tf_vars = []
        tf_lists = []
        for interpolation in interpolations:
            new_vars = var_pattern.findall(interpolation[1])
            tf_vars += new_vars
            if interpolation[0]:  # see if it looks like a list
                tf_lists += new_vars

        tf_vars = list(dict.fromkeys(tf_vars))
        tf_lists = list(dict.fromkeys(tf_lists))

        return {'vars': tf_vars, 'lists': tf_lists}

    def find_vars_in_file(self, phrase, token):
        """Extract vars from .tf file."""

        var_dict = BassExtractor.find_vars(
            BassExtractor.get_file_contents(self.args.input),
            phrase,
            token)

        if self.args.asc:
            var_dict['vars'].sort()
        elif self.args.desc:
            var_dict['vars'].sort(reverse=True)

        self.tf_vars = var_dict['vars']
        self.tf_lists = var_dict['lists']


class VarExtractor(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files to make creating
    Terraform modules easier.
    """
    def __init__(self, args):
        """Instantiate"""
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
                if tf_var in self.tf_lists:
                    file_handle.write('  type        = "list"\n')
                    file_handle.write('  default     = []\n')
                else:
                    file_handle.write('  type        = "string"\n')
                    file_handle.write('  default     = ""\n')
                file_handle.write('}\n\n')

    def extract(self):
        """Extract vars from .tf file."""
        self.find_vars_in_file(self.main_phrase_find, self.main_token_find)
        self.write_file()

        return EXIT_OKAY


class StubMaker(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files and creates a
    module-use stub.
    """
    def __init__(self, args):
        """Instantiate"""
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
        self.find_vars_in_file(self.var_phrase_find, self.var_token_find)
        self.write_file()

        return EXIT_OKAY


class Checker(BassExtractor):
    """
    A class that extracts variables from Terraform HCL files and checks them.
    """
    def __init__(self, args):
        """Instantiate"""
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
                if tf_var in self.tf_lists:
                    file_handle.write('  type        = "list"\n')
                    file_handle.write('  default     = []\n')
                else:
                    file_handle.write('  type        = "string"\n')
                    file_handle.write('  default     = ""\n')
                file_handle.write('}\n')

    def find_missing(self):
        """Find missing vars in .tf files."""
        main_vars = self.find_vars(
            self.get_file_contents(self.args.input),
            self.main_phrase_find,
            self.main_token_find)

        var_vars = self.find_vars(
            self.get_file_contents(self.args.output),
            self.var_phrase_find,
            self.var_token_find)

        return {
            'main': list(set(main_vars['vars']) - set(var_vars['vars'])),
            'var': list(set(var_vars['vars']) - set(main_vars['vars']))
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
