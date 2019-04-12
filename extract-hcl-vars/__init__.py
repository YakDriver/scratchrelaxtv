# -*- coding: utf-8 -*-
"""scratchrelaxtv module.

This module helps in generating standalone applications from python
packages using PyInstaller.

The basic functionality of Gravity Bee was laid out by
Nicholas Chammas (@nchammas) in a project called FlintRock.

Example:
    Help using the scratchrelaxtv CLI can be found by typing the following::

        $ scratchrelaxtv --help
"""

import logging
import logging.config
import os
import platform
import shutil
import subprocess
from string import Template


__version__ = "0.1.0"
EXIT_OKAY = 0
EXIT_NOT_OKAY = 1
FILE_DIR = ".scratchrelaxtv"

logging.config.fileConfig(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))
logger = logging.getLogger(__name__)        # pylint: disable=invalid-name


class Arguments():
    """
    A class representing the configuration information needed by the
    scratchrelaxtv.PackageGenerator class.

    Attributes:
        flags: A dict of bools for flags including "clean" (T: whether to clean
            after generation), "dont_write_file" (F: whether to write files),
            "one_dir" (F: whether to package as a directory or app),
            "with_latest" (F: whether to also create a "latest" dir).
        directories: A dict of strings for directories used in generation
            including "pkg" (where setup.py lives), "src" (path to source),
            "work" (where work files will be put), "staging" (where artifacts
            are staged).
        formats: A dict of strings for output formats in the str.format()
            notation including "name" (format used in naming generated
            application), "sha" (format used in naming generated SHA file for
            the application), "label" (format used for generated application's
            label).
        extra: A dict of strings for extra material to include with the
            generated application including "data" (data to include), "pkgs"
            (extra packages to include in the application), "modules" (extra
            modules to include in the application).
        info: A dict of strings with general information about the process
            including "sha" (enumeration to specify creating a file with the
            SHA hash or just include in output information), "console_scripts"
            (where the existing app's console scripts are located),
            "app_version" (the version of the app), "app_name" (name of the
            app), "pkg_name" (name of the package the existing app lives in),
            "script_path" (path to the script installed by pip),
            "operating_system" (operating system currently running),
            "machine_type" (machine type currently running).
        pyppy: An instance of pyppyn.ConfigRep for gathering application
            information.
    """

    OPTION_SHA_INFO = "info"
    OPTION_SHA_FILE = "file"

    def __init__(self, **kwargs):
        """Instantiation"""

        if not os.environ.get('VIRTUAL_ENV'):
            logger.error("No virtual environment directory detected!")
            raise NotADirectoryError

        # Remove unused options
        empty_keys = [key for key, value in kwargs.items() if not value]
        for key in empty_keys:
            del kwargs[key]

        # arguments that do NOT depend on pyppyn
        self.flags = {}
        self.flags["clean"] = kwargs.get('clean', False)

        self.directories = {}
        self.directories["pkg"] = kwargs.get(
            'pkg_dir',
            os.environ.get(
                'GB_PKG_DIR',
                '.'
            )
        )

        self.directories["src"] = kwargs.get(
            'src_dir',
            os.environ.get(
                'GB_SRC_DIR',
                '.'
            )
        )

        self.formats = {}
        self.formats["name"] = kwargs.get(
            'name_format',
            os.environ.get(
                'GB_NAME_FORMAT',
                '{an}-{v}-standalone-{os}-{m}'
            )
        )

        self.formats["sha"] = kwargs.get(
            'sha_format',
            os.environ.get(
                'GB_SHA_FORMAT',
                '{an}-{v}-sha256-{os}-{m}.json'
            )
        )

        self.formats["label"] = kwargs.get(
            'label_format',
            os.environ.get(
                'GB_LABEL_FORMAT',
                '{An} {v} {ft} for {os} [scratchrelaxtv Build]'
            )
        )

        self.extra = {}
        self.extra["data"] = kwargs.get(
            'extra_data',
            None
        )

        self.extra["pkgs"] = kwargs.get(
            'extra_pkgs',
            []
        )

        self.extra["modules"] = kwargs.get(
            'extra_modules',
            []
        )

        self.flags["dont_write_file"] = kwargs.get(
            'no_file',
            False
        )

        self.directories["work"] = kwargs.get(
            'work_dir',
            os.environ.get(
                'GB_WORK_DIR',
                os.path.join(
                    FILE_DIR,
                    'build',
                    uuid.uuid1().hex[:16]
                )
            )
        )

        if os.path.exists(self.directories["work"]):
            logger.error("work_dir must not exist. It may be deleted.")
            raise FileExistsError

        self.flags["one_dir"] = kwargs.get(
            'onedir',
            os.environ.get(
                'GB_ONEDIR',
                False
            )
        )

        self.directories["staging"] = kwargs.get(
            'staging_dir',
            os.environ.get(
                'GB_STAGING_DIR',
                os.path.join(FILE_DIR, 'dist')
            )
        )

        self.flags["with_latest"] = kwargs.get(
            'with_latest',
            False
        )

        self.info = {}
        self.info["sha"] = kwargs.get(
            'sha',
            Arguments.OPTION_SHA_INFO
        )

        # arguments that DO depend on pyppyn
        self.pyppy = pyppyn.ConfigRep(setup_path=self.directories["pkg"])

        self.info["console_script"] = self.pyppy.get_config_attr(
            'console_scripts'
        )
        self.info["app_version"] = self.pyppy.get_config_attr('version')

        # Initial values
        self.info["app_name"] = kwargs.get(
            'app_name',
            os.environ.get(
                'GB_APP_NAME',
                self.pyppy.config['app_name']
            )
        )

        self.info["pkg_name"] = kwargs.get(
            'pkg_name',
            os.environ.get(
                'GB_PKG_NAME',
                self.pyppy.get_config_attr('packages')
            )
        )

        self.info["script_path"] = kwargs.get(
            'script_path',
            os.environ.get(
                'GB_SCRIPT',
                self.find_script()
            )
        )

        pl_sys = platform.system().lower()
        self.info["operating_system"] = pl_sys if pl_sys != 'darwin' else 'osx'

        self.info["machine_type"] = platform.machine().lower()

        self.run_info()

    def run_info(self):
        """Log all the attributes of this run."""
        logger.info("Arguments:")
        logger.info("app_name: %s", self.info["app_name"])
        logger.info("app_version: %s", self.info["app_version"])
        logger.info("operating_system: %s", self.info["operating_system"])
        logger.info("machine_type: %s", self.info["machine_type"])
        logger.info("console_script: %s", self.info["console_script"])
        logger.info("pkg_name: %s", self.info["pkg_name"])
        logger.info("script_path: %s", self.info["script_path"])
        logger.info("pkg_dir: %s", self.directories["pkg"])
        logger.info("src_dir: %s", self.directories["src"])
        logger.info("name_format: %s", self.formats["name"])
        logger.info("clean: %s", self.flags["clean"])
        logger.info("work_dir: %s", self.directories["work"])
        logger.info("onedir: %s", self.flags["one_dir"])
        logger.info("staging_dir: %s", self.directories["staging"])
        logger.info("with_latest: %s", self.flags["with_latest"])
        logger.info("sha: %s", self.info["sha"])

        if self.extra["data"] is not None:
            for extra_data in self.extra["data"]:
                logger.info("extra_data: %s", extra_data)

    def find_script(self):
        """Search likely places to find the console script for app."""
        # Windows example: C:\venv\Scripts\<console-script>-script.py

        possible_paths = []

        # likely posix
        possible_paths.append(os.path.join(
            os.environ.get('VIRTUAL_ENV'),
            'bin',
            self.info["console_script"]
        ))

        # likely windows
        possible_paths.append(os.path.join(
            os.environ.get('VIRTUAL_ENV'),
            'Scripts',
            self.info["console_script"] + '-script.py'
        ))

        # other windows
        possible_paths.append(os.path.join(
            os.environ.get('VIRTUAL_ENV'),
            'Scripts',
            self.info["console_script"] + '.py'
        ))

        # unlikely posix
        possible_paths.append(os.path.join(
            os.environ.get('VIRTUAL_ENV'),
            'bin',
            self.info["console_script"] + '-script.py'
        ))

        # without virtual env dir
        possible_paths.append(os.path.join(
            'bin',
            self.info["console_script"]
        ))

        possible_paths.append(os.path.join(
            'bin',
            self.info["console_script"] + '-script.py'
        ))

        possible_paths.append(os.path.join(
            'Scripts',
            self.info["console_script"] + '-script.py'
        ))

        possible_paths.append(os.path.join(
            'Scripts',
            self.info["console_script"]
        ))

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None


class PackageGenerator():
    """
    Utility for generating standalone executable versions of python
    programs that are already packaged in a standard setuptools
    package.

    Attributes:
        args: An instance of scratchrelaxtv.Arguments containing
            the configuration information for scratchrelaxtv.
        operating_system: A str of the os. This is automatically
            determined.
        machine_type: A str of the machine (e.g., x86_64)
        standalone_name: A str that will be the name of the
            standalone application.
        gb_dir: A str of the scratchrelaxtv runtime package directory.
        gb_filename: A str of the runtime filename.
        gen_file: A str with name of file of the standalone
            application created.
        gen_file_w_path: A str with absolute path and name of file of
            the standalone application created.
        sha_file: A str with name of file to use in generating the SHA.
        file_sha: A str with hash of the sha_file file.
    """

    ENVIRON_PREFIX = 'GB_ENV_'
    INFO_FILE = os.path.join(FILE_DIR, 'scratchrelaxtv-info.json')
    FILES_FILE = os.path.join(FILE_DIR, 'scratchrelaxtv-files.json')
    ENVIRON_SCRIPT = os.path.join(FILE_DIR, 'scratchrelaxtv-environs')
    ENVIRON_SCRIPT_POSIX_EXT = '.sh'
    ENVIRON_SCRIPT_WIN_EXT = '.bat'
    ENVIRON_SCRIPT_POSIX_ENCODE = 'utf-8'
    ENVIRON_SCRIPT_WIN_ENCODE = 'cp1252'

    # 'html.parser' hidden import is introduced by botocore.
    # We won't need this when this issue is resolved:
    # https://github.com/pyinstaller/pyinstaller/issues/1844

    # 'configparser' hidden import is also introduced by botocore.
    # It appears to be related to this issue:
    # https://github.com/pyinstaller/pyinstaller/issues/1935

    EXTRA_REQD_PACKAGES = [
        # 'packaging',
        # 'configparser',
        # 'setuptools'
    ]

    EXTRA_REQD_MODULES = [
        # 'packaging',
        # 'configparser',
        # 'packaging.version',
        # 'packaging.specifiers',
        # 'pkg_resources',
        # 'html.parser',
        # 'distutils'
    ]

    @classmethod
    def get_hash(cls, filename):
        """
        Finds a SHA256 for the given file.

        Args:
            filename: A str representing a file.
        """

        if os.path.exists(filename):
            sha256 = hashlib.sha256()
            with open(filename, "rb") as file_to_hash:
                for chunk in iter(lambda: file_to_hash.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()

        return None

    def __init__(self, args=None):

        self.args = args

        self.files = {}

        self.files["gen"] = None            # not set until file is created
        self.files["gen_w_path"] = None     # not set until file is created
        self.files["sha"] = None            # not set until file is created
        self.files["sha_w_path"] = None     # not set until file is created
        self.files["hook"] = None
        self.file_sha = None

        self.standalone_name = self.args.formats["name"].format(
            an=self.args.info["app_name"],
            v=self.args.info["app_version"],
            os=self.args.info["operating_system"],
            m=self.args.info["machine_type"]
        )

        self.gb_dir, self.gb_filename = os.path.split(__file__)

        if not os.path.exists(self.args.directories["work"]):
            os.makedirs(self.args.directories["work"])

        if not os.path.exists(
                os.path.join(self.args.directories["work"], 'hooks')):
            os.makedirs(os.path.join(self.args.directories["work"], 'hooks'))

        if not os.path.exists(FILE_DIR):
            os.makedirs(FILE_DIR)

        self._temp_script = os.path.join(
            self.args.directories["work"],
            uuid.uuid1().hex[:16] + '_'
            + self.args.info["console_script"] + '.py'
        )

        logger.info("Package generator:")
        logger.info("standalone_name: %s", self.standalone_name)

    def _create_hook(self):
        # get the hook ready
        template = Template(
            open(
                os.path.join(
                    self.gb_dir,
                    "hook-template"
                ),
                "r"
            ).read()
        )

        hook = template.safe_substitute(
            {'app_name': self.args.info["app_name"]})

        # 1 - extra data
        hook += "# collection extra data, if any (using --extra-data option)"
        for data in self.args.extra["data"]:
            hook += "\ndatas.append(('"
            hook += self.args.directories["pkg"] + os.sep
            if self.args.directories["src"] != '.':
                hook += self.args.directories["src"] + os.sep
            hook += self.args.info["pkg_name"] + os.sep + data
            hook += "', '" + self.args.info["pkg_name"] + "/" + data + "'))"
            hook += "\n\n"

        # 2 - package metadata
        hook += "# add dependency metadata"
        for package in self.args.pyppy.get_required():
            # datas += copy_metadata(pkg)
            hook += "\ndatas += copy_metadata('" + package + "')"

        hook += "\n"

        # 3 - write file
        self.files["hook"] = os.path.join(
            self.args.directories["work"],
            'hooks',
            "hook-" + self.args.info["pkg_name"] + ".py"
        )
        hook_file = open(self.files["hook"], "w+")
        hook_file.write(hook)
        hook_file.close()

        logger.info("Created hook file: %s", self.files["hook"])

    def _process_sha(self):

        logger.info("Processing SHA256 hash info...")

        if self.args.flags["one_dir"]:
            logger.info(
                "In onedir mode, no SHA256 hash can be created."
            )
        else:

            self.file_sha = PackageGenerator.get_hash(self.files["gen_w_path"])

            if self.args.info["sha"] == Arguments.OPTION_SHA_FILE:

                # in memory version of file contents
                sha_dict = {}
                sha_dict[self.files["gen"]] = self.file_sha

                # file name
                self.files["sha"] = self.args.formats["sha"].format(
                    an=self.args.info["app_name"],
                    v=self.args.info["app_version"],
                    os=self.args.info["operating_system"],
                    m=self.args.info["machine_type"]
                )

                logger.info("SHA256 hash file: %s", self.files["sha"])

                sha_file = open(self.files["sha"], 'w')
                sha_file.write(json.dumps(sha_dict))
                sha_file.close()

    def _stage_artifacts(self):

        logger.info("Staging artifacts...")

        # create directories
        if os.path.exists(self.args.directories["staging"]):
            logger.info(
                "Removing staging directory: %s",
                self.args.directories["staging"])
            shutil.rmtree(self.args.directories["staging"])

        os.makedirs(self.args.directories["staging"])

        # version-based dir
        version_dst = os.path.join(
            self.args.directories["staging"],
            self.args.info["app_version"]
        )
        if not os.path.exists(version_dst):
            os.makedirs(version_dst)

        shutil.move(self.files["gen_w_path"], version_dst)

        # update path
        self.files["gen_w_path"] = os.path.join(
            version_dst,
            self.files["gen"]
        )

        logger.info("Main artifact: %s", self.files["gen_w_path"])

        # dir just called 'latest'
        if self.args.flags["with_latest"]:

            logger.info("Creating latest dir...")

            latest_dst = os.path.join(
                self.args.directories["staging"],
                'latest'
            )
            if not os.path.exists(latest_dst):
                os.makedirs(latest_dst)

            logger.info("Copying to latest...")

            if self.args.flags["one_dir"]:
                shutil.copytree(
                    self.files["gen_w_path"],
                    os.path.join(latest_dst, self.files["gen"])
                )
            else:
                shutil.copy2(self.files["gen_w_path"], latest_dst)

            latest_standalone_name = self.args.formats["name"].format(
                an=self.args.info["app_name"],
                v='latest',
                os=self.args.info["operating_system"],
                m=self.args.info["machine_type"]
            )

            if self.files["gen"].endswith(".exe"):
                latest_standalone_name += ".exe"

            os.rename(
                os.path.join(latest_dst, self.files["gen"]),
                os.path.join(latest_dst, latest_standalone_name)
            )

            logger.info(
                "Latest artifact: %s",
                os.path.join(latest_dst, latest_standalone_name)
            )

        if self.args.info["sha"] == Arguments.OPTION_SHA_FILE \
                and not self.args.flags["one_dir"]:

            logger.info("Staging SHA hash artifact: %s", self.files["sha"])

            shutil.move(self.files["sha"], version_dst)

            self.files["sha_w_path"] = os.path.join(
                version_dst,
                self.files["sha"]
            )

            logger.info("SHA artifact: %s", self.files["sha_w_path"])

            if self.args.flags["with_latest"]:

                shutil.copy2(self.files["sha_w_path"], latest_dst)

                latest_sha_file = self.args.formats["sha"].format(
                    an=self.args.info["app_name"],
                    v='latest',
                    os=self.args.info["operating_system"],
                    m=self.args.info["machine_type"]
                )

                os.rename(
                    os.path.join(latest_dst, self.files["sha"]),
                    os.path.join(latest_dst, latest_sha_file)
                )

                logger.info(
                    "Latest SHA artifact: %s",
                    os.path.join(latest_dst, latest_sha_file)
                )

    def _gather_info(self):
        # GATHER INFO -------------------------------------------
        gb_info = {}
        gb_info['app_name'] = self.args.info["app_name"]
        gb_info['app_version'] = self.args.info["app_version"]
        gb_info['operating_system'] = self.args.info["operating_system"]
        gb_info['machine_type'] = self.args.info["machine_type"]
        gb_info['console_script'] = self.args.info["console_script"]
        gb_info['script_path'] = self.args.info["script_path"]
        gb_info['pkg_dir'] = self.args.directories["pkg"]
        gb_info['src_dir'] = self.args.directories["src"]
        gb_info['name_format'] = self.args.formats["name"]
        gb_info['clean'] = self.args.flags["clean"]
        gb_info['work_dir'] = self.args.directories["work"]
        gb_info['onedir'] = self.args.flags["one_dir"]
        gb_info['staging_dir'] = self.args.directories["staging"]
        gb_info['with_latest'] = self.args.flags["with_latest"]
        gb_info['gen_file'] = self.files["gen"]
        gb_info['gen_file_w_path'] = self.files["gen_w_path"]

        if not self.args.flags["one_dir"]:
            gb_info['file_sha'] = self.file_sha

        if self.args.info["sha"] == Arguments.OPTION_SHA_FILE \
                and not self.args.flags["one_dir"]:
            gb_info['sha_file'] = self.files["sha"]
            gb_info['sha_file_w_path'] = self.files["sha_w_path"]
            gb_info['sha_format'] = self.args.formats["sha"]

        gb_info['extra_data'] = []

        if self.args.extra["data"] is not None:
            for extra_data in self.args.extra["data"]:
                gb_info['extra_data'].append(extra_data)

        # INFO file ---------------------------------------------
        logger.info(
            "Writing information file: %s",
            PackageGenerator.INFO_FILE
        )
        info_file = open(PackageGenerator.INFO_FILE, 'w')
        info_file.write(json.dumps(gb_info))
        info_file.close()

        return gb_info

    def _write_info_files(self):

        if not self.args.flags["dont_write_file"]:

            gb_info = self._gather_info()

            # FILES file --------------------------------------------

            # create memory structure
            gb_files = []
            gb_file = {}
            gb_file['filename'] = self.files["gen"]
            gb_file['path'] = self.files["gen_w_path"]
            if self.files["gen"].endswith(".exe"):
                gb_file['mime-type'] = \
                    'application/vnd.microsoft.portable-executable'
            else:
                gb_file['mime-type'] = 'application/x-executable'
            os_label = self.args.info["operating_system"].title()
            if self.args.info["operating_system"] == 'osx':
                os_label = self.args.info["operating_system"].upper()
            gb_file['label'] = self.args.formats["label"].format(
                An=self.args.info["app_name"].title(),
                an=self.args.info["app_name"],
                v=self.args.info["app_version"],
                os=os_label,
                m=self.args.info["machine_type"],
                ft="Standalone Executable"
            )
            gb_files.append(gb_file)

            if self.args.info["sha"] == Arguments.OPTION_SHA_FILE \
                    and not self.args.flags["one_dir"]:

                sha_file_info = {}
                sha_file_info['filename'] = self.files["sha"]
                sha_file_info['path'] = self.files["sha_w_path"]
                sha_file_info['mime-type'] = 'application/json'
                sha_file_info['label'] = self.args.formats["label"].format(
                    An=self.args.info["app_name"].title(),
                    an=self.args.info["app_name"],
                    v=self.args.info["app_version"],
                    os=os_label,
                    m=self.args.info["machine_type"],
                    ft="Standalone Executable SHA256 Hash"
                )
                gb_files.append(sha_file_info)

            # write to disk
            logger.info(
                "Writing files file: %s",
                PackageGenerator.FILES_FILE
            )
            file_file = open(PackageGenerator.FILES_FILE, 'w')
            file_file.write(json.dumps(gb_files))
            file_file.close()

            # ENVIRONS ----------------------------------------------

            # remove attributes that aren't useful as exported
            # environs
            del gb_info['extra_data']
            del gb_info['name_format']
            del gb_info['clean']

            try:
                del gb_info['sha_format']
            except KeyError:
                pass

            logger.info(
                "Writing environ script: %s",
                PackageGenerator.ENVIRON_SCRIPT
                + PackageGenerator.ENVIRON_SCRIPT_POSIX_EXT
            )
            shell = open(
                PackageGenerator.ENVIRON_SCRIPT
                + PackageGenerator.ENVIRON_SCRIPT_POSIX_EXT,
                mode='w',
                encoding=PackageGenerator.ENVIRON_SCRIPT_POSIX_ENCODE
            )

            for key, value in gb_info.items():
                shell.write("export ")
                shell.write(PackageGenerator.ENVIRON_PREFIX + key.upper())
                shell.write('="')
                shell.write(str(value))
                shell.write('"\n')

            shell.close()

            logger.info(
                "Writing environ script: %s%s",
                PackageGenerator.ENVIRON_SCRIPT,
                PackageGenerator.ENVIRON_SCRIPT_WIN_EXT
            )

            bat = open(
                PackageGenerator.ENVIRON_SCRIPT
                + PackageGenerator.ENVIRON_SCRIPT_WIN_EXT,
                mode='w',
                encoding=PackageGenerator.ENVIRON_SCRIPT_WIN_ENCODE
            )

            for key, value in gb_info.items():
                bat.write("set ")
                bat.write(PackageGenerator.ENVIRON_PREFIX + key.upper())
                bat.write("=")
                bat.write(str(value))
                bat.write("\r\n")

            bat.close()

    def _cleanup(self):

        if self.args.flags["clean"]:
            logger.info("Cleaning up...")

            # clean work dir

            if os.path.isdir(self.args.directories["work"]):
                logger.info(
                    "Deleting working dir: %s",
                    self.args.directories["work"])
                shutil.rmtree(self.args.directories["work"])

    def generate(self):
        """Generate the standalone application."""
        self._create_hook()

        replace_venv_distutils()

        try:
            shutil.copy2(self.args.info["script_path"], self._temp_script)
        except FileNotFoundError:
            logger.error(
                "application script not found: %s",
                "\n1. Run scratchrelaxtv in a virtual env" +
                "\n2. Use the --script option" +
                "\n3. Install your application using pip" +
                "\n4. Make sure your application has a console " +
                "script entry in setup.py or setup.cfg."
            )
            self._cleanup()
            return False

        commands = [
            'pyinstaller',
            '--noconfirm',
            '--name', self.standalone_name,
            '--paths', self.args.directories["src"],
            '--additional-hooks-dir', os.path.join(
                self.args.directories["work"], 'hooks'),
            '--specpath', self.args.directories["work"],
            '--workpath', os.path.join(self.args.directories["work"], 'build'),
            '--distpath', os.path.join(self.args.directories["work"], 'dist'),
            '--hidden-import', self.args.info["pkg_name"],
        ]

        insert_point = commands.index('--noconfirm') + 1
        if self.args.flags["one_dir"]:
            commands[insert_point:insert_point] = ['--onedir', '--debug']
        else:
            commands[insert_point:insert_point] = ['--onefile']

        insert_point = commands.index('--noconfirm') + 1
        if self.args.flags["clean"]:
            commands[insert_point:insert_point] = ['--clean']

        for extra_package in list(
                set(self.EXTRA_REQD_PACKAGES) | set(self.args.extra["pkgs"])
        ):
            if extra_package not in self.args.pyppy.get_required():
                pyppyn.ConfigRep.install_package(extra_package)

        for extra_module in list(
                set(self.EXTRA_REQD_MODULES) | set(self.args.extra["modules"])
        ):
            commands += ['--hidden-import', extra_module]

        commands += [
            self._temp_script
        ]

        if self.args.info["operating_system"] != 'windows':
            insert_point = commands.index('--noconfirm') + 1
            commands[insert_point:insert_point] = ['--runtime-tmpdir', '.']

        logger.info("PyInstaller commands:")
        logger.info(", ".join(commands))

        subproc_args = {}
        subproc_args['check'] = False

        subproc_args['stdout'] = subprocess.PIPE
        subproc_args['stderr'] = subprocess.PIPE

        result = subprocess.run(commands, **subproc_args)

        if result.stdout:
            logger.debug(result.stdout.decode('utf-8'))

        if result.stderr and result.stderr != result.stdout:
            logger.error(result.stderr.decode('utf-8'))

        unreplace_venv_distutils()

        if result.returncode != 0:
            logger.error(
                "PyInstaller exited with error code %s", result.returncode)
            return EXIT_NOT_OKAY

        # get info about standalone binary
        for standalone in glob.glob(
                os.path.join(
                    self.args.directories["work"],
                    'dist',
                    self.standalone_name + '*'
                )):
            self.files["gen_w_path"] = standalone
            self.files["gen"] = os.path.basename(self.files["gen_w_path"])
            logger.info("Generated standalone file: %s", self.files["gen"])

        self._process_sha()         # creates the sha files need for staging
        self._stage_artifacts()     # creates the file names needed to write
        self._write_info_files()    # write info (with paths) and sha
        self._cleanup()
        return EXIT_OKAY
