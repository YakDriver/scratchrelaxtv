# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""test_scratchrelaxtv module."""
import glob
import os
import json

from subprocess import check_output

import pytest
from scratchrelaxtv import Arguments, PackageGenerator, EXIT_OKAY, FILE_DIR


# should be first so that other tests haven't created files
def test_no_output():
    """Makes sure that when no output flag is on, no files are created."""
    args = Arguments(
        src_dir="src",
        extra_data=["gbextradata"],
        pkg_dir=os.path.join("tests", "gbtestapp"),
        clean=True,
        no_file=True
    )
    package_generator = PackageGenerator(args)
    generated_okay = package_generator.generate()

    sha_filename = package_generator.args.formats["sha"].format(
        an=package_generator.args.info['app_name'],
        v=package_generator.args.info['app_version'],
        os=package_generator.args.info['operating_system'],
        m=package_generator.args.info['machine_type']
    )

    assert generated_okay == EXIT_OKAY \
        and not os.path.exists(PackageGenerator.INFO_FILE) \
        and not os.path.exists(PackageGenerator.FILES_FILE) \
        and not os.path.exists(PackageGenerator.ENVIRON_SCRIPT
                               + PackageGenerator.ENVIRON_SCRIPT_POSIX_EXT) \
        and not os.path.exists(PackageGenerator.ENVIRON_SCRIPT
                               + PackageGenerator.ENVIRON_SCRIPT_WIN_EXT) \
        and not os.path.exists(sha_filename)


# should be second so there are still not output files
def test_no_output_but_sha():
    """Makes sure that when no output flag is on, no files are created."""
    args = Arguments(
        src_dir="src",
        extra_data=["gbextradata"],
        pkg_dir=os.path.join("tests", "gbtestapp"),
        sha=Arguments.OPTION_SHA_FILE,
        clean=True,
        no_file=True
    )
    package_generator = PackageGenerator(args)
    generated_okay = package_generator.generate()

    assert generated_okay == EXIT_OKAY \
        and not os.path.exists(PackageGenerator.INFO_FILE) \
        and not os.path.exists(PackageGenerator.FILES_FILE) \
        and not os.path.exists(PackageGenerator.ENVIRON_SCRIPT
                               + PackageGenerator.ENVIRON_SCRIPT_POSIX_EXT) \
        and not os.path.exists(PackageGenerator.ENVIRON_SCRIPT
                               + PackageGenerator.ENVIRON_SCRIPT_WIN_EXT) \
        and os.path.exists(package_generator.files["sha_w_path"])


# test extra_pkgs and extra_modules
def test_extra_pkgs_modules():
    """Makes sure everything works with an extra package and module."""
    args = Arguments(
        src_dir="src",
        extra_data=["gbextradata"],
        pkg_dir=os.path.join("tests", "gbtestapp"),
        clean=False,
        extra_pkgs=["PyYAML"],
        extra_modules=["yaml"],
    )
    package_generator = PackageGenerator(args)
    generated_okay = package_generator.generate()

    assert generated_okay == EXIT_OKAY


@pytest.fixture
def arguments():
    """Returns an Arguments instance using the included app"""
    return Arguments(
        src_dir="src",
        extra_data=["gbextradata"],
        pkg_dir=os.path.join("tests", "gbtestapp"),
        sha=Arguments.OPTION_SHA_FILE,
        clean=True
    )


def test_generation(arguments):
    """ Tests generating the executable. """
    package_generator = PackageGenerator(arguments)
    generated_okay = package_generator.generate()

    assert generated_okay == EXIT_OKAY


def test_executable(arguments):
    """ Tests running the executable. """
    package_generator = PackageGenerator(arguments)
    generated_okay = package_generator.generate()
    if generated_okay == EXIT_OKAY:
        files = glob.glob(os.path.join(
            package_generator.args.directories['staging'],
            package_generator.args.info['app_version'],
            'gbtestapp-4.2.6-standalone*'
        ))

        cmd_output = check_output(files[0], universal_newlines=True)
        compare_file = open(os.path.join(
            "tests",
            "gbtestapp",
            "correct_stdout.txt"), "r").read()

        assert cmd_output == compare_file
    else:
        assert False


def test_filename_file(arguments):
    """ Tests if scratchrelaxtv writes name of standalone app in output. """
    package_generator = PackageGenerator(arguments)
    generated_okay = package_generator.generate()
    if generated_okay == EXIT_OKAY:
        sa_file = open(
            os.path.join(
                FILE_DIR,
                "scratchrelaxtv-files.json"
            ), "r"
        )
        gb_files = json.loads(sa_file.read())
        sa_file.close()

        assert gb_files[0]['filename'].startswith("gbtestapp-4.2.6-standalone")
    else:
        assert False


def test_file_label():
    """ Test if scratchrelaxtv writes correct label in scratchrelaxtv-files.json. """

    label_prefix = "GBTESTapp YO"
    arguments = Arguments(
        src_dir="src",
        extra_data=["gbextradata"],
        pkg_dir=os.path.join("tests", "gbtestapp"),
        sha=Arguments.OPTION_SHA_FILE,
        clean=True,
        label_format=label_prefix + " {v} {ft} for {os}"
    )
    package_generator = PackageGenerator(arguments)
    generated_okay = package_generator.generate()
    if generated_okay == EXIT_OKAY:
        sa_file = open(
            os.path.join(
                FILE_DIR,
                "scratchrelaxtv-files.json"
            ), "r"
        )
        gb_files = json.loads(sa_file.read())
        sa_file.close()

        assert gb_files[0]['label'].startswith(label_prefix)
    else:
        assert False


def test_file_sha(arguments):
    """
    Checks the generated sha hash written to file with one that is
    freshly calculated. Also checks that info file exists and has the
    correct app name and version.
    """

    # get the sha256 hash from the json file
    package_generator = PackageGenerator(arguments)
    generated_okay = package_generator.generate()
    if generated_okay == EXIT_OKAY:
        # get the info from info file
        info_file = open(PackageGenerator.INFO_FILE, "r")
        info = json.loads(info_file.read())
        info_file.close()

        sha_file = open(package_generator.files["sha_w_path"], "r")
        sha_dict = json.loads(sha_file.read())
        sha_file.close()

        assert info['file_sha'] \
            == PackageGenerator.get_hash(info['gen_file_w_path']) \
            == sha_dict[info['gen_file']]
    else:
        assert False


@pytest.fixture
def latest_arguments():
    """Returns an Arguments instance using the included app"""
    return Arguments(
        src_dir="src",
        extra_data=["gbextradata"],
        pkg_dir=os.path.join("tests", "gbtestapp"),
        sha=Arguments.OPTION_SHA_FILE,
        clean=True,
        with_latest=True
    )


def test_latest(latest_arguments):
    """
    Checks to make sure the latest directory is created and
    populated with standalone executable and SHA.
    """

    package_generator = PackageGenerator(latest_arguments)
    generated_okay = package_generator.generate()

    if generated_okay == EXIT_OKAY:

        latest_standalone = package_generator.args.formats["name"].format(
            an=package_generator.args.info['app_name'],
            v='latest',
            os=package_generator.args.info['operating_system'],
            m=package_generator.args.info['machine_type']
        )

        sa_files = glob.glob(os.path.join(
            package_generator.args.directories['staging'],
            'latest',
            latest_standalone + '*'
        ))

        sha_file = package_generator.args.formats["sha"].format(
            an=package_generator.args.info['app_name'],
            v='latest',
            os=package_generator.args.info['operating_system'],
            m=package_generator.args.info['machine_type']
        )

        sha_files = glob.glob(os.path.join(
            package_generator.args.directories['staging'],
            'latest',
            sha_file
        ))

        assert os.path.isdir(os.path.join(
            package_generator.args.directories['staging'],
            'latest')) \
            and sa_files \
            and sha_files
    else:
        assert False


@pytest.fixture
def testing_defaults():
    """Return an Arguments instance for testing defaults"""
    if not os.getcwd().endswith(os.path.join("tests", "gbtestapp")):
        os.chdir(os.path.join("tests", "gbtestapp"))
    return Arguments()


def test_clean(testing_defaults):
    """Test clean default"""
    assert not testing_defaults.flags["clean"]


def test_pkg_dir(testing_defaults):
    """Test pkg_dir default"""
    assert testing_defaults.directories["pkg"] == '.'


def test_src_dir(testing_defaults):
    """Test src_dir default"""
    assert testing_defaults.directories["src"] == '.'


def test_name_format(testing_defaults):
    """Test name_format default"""
    assert testing_defaults.formats["name"] == '{an}-{v}-standalone-{os}-{m}'


def test_sha_format(testing_defaults):
    """Test sha_format default"""
    assert testing_defaults.formats["sha"] == '{an}-{v}-sha256-{os}-{m}.json'


def test_extra_data(testing_defaults):
    """Test extra data default"""
    assert testing_defaults.extra["data"] is None


def test_work_dir(testing_defaults):
    """Test work_dir default"""
    assert testing_defaults.directories["work"][:17] == os.path.join(
        FILE_DIR,
        'build')[:17]


def test_console_script(testing_defaults):
    """Test console_script default"""
    assert testing_defaults.info["console_script"] == 'gbtestapp'


def test_app_version(testing_defaults):
    """Test app_version default"""
    assert testing_defaults.info["app_version"] == '4.2.6'


def test_app_name(testing_defaults):
    """Test app_name default"""
    assert testing_defaults.info["app_name"] == 'gbtestapp'


def test_pkg_name(testing_defaults):
    """Test pkg_name default"""
    assert testing_defaults.info["pkg_name"] == 'gbtestapp'
