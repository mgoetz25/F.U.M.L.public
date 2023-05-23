"""
When this script is run, it will run the tests in the desired directory of
test scripts. Each test script contains tests and is expected to do anything
to test the programs functionality; test scripts may stop execution, report
errors, or do whatever because it is not the concern of this script.

Given the test directory, this script will RECURSIVELY go through all of the
files with a provided file extension and will ignore any files with a suffix
specified in the call to main's test_ign.

Because this script is intended to be ran, this script's location is added
to PYTHONPATH for the session. Therefore, all imports of the test scripts
are expected to be absolute imports relative to the root of this project.
Which is good practice according to PEP 8 (https://pep8.org/#imports)
"""

import os
import sys
import subprocess
import functools

# edit these if you want.
# you can add your own directories where some tests are located.
TEST_DIRS = ["fuml/tests"]
TEST_EXT = ".py"
TEST_IGN = ["__init__.py"]


def main(test_dirs, test_ext, test_ign):
    for test_dir in test_dirs:
        # get all of the filenames in the test directory
        all_files = get_files_recursively(test_dir)

        # filter it to get only filenames that end in a given extension
        test_files = filter(lambda fn: fn.lower().endswith(test_ext), all_files)

        # ignore any ignored files
        for ign in test_ign:
            test_files = filter(lambda fn: not fn.lower().endswith(ign), test_files)

        # now test the scripts that are gathered.
        print("")
        for test_fn in test_files:
            # for each test, set up the PYTHONPATH variable to be at the root of the project.
            # first, copy the current environment variables.
            environment_copy = os.environ.copy()
            # then add the current directory as a place to search for modules.
            path_sep = os.pathsep   # get the path separator first for the system (Unix=:, Windows=;)
            environment_copy["PYTHONPATH"] = functools.reduce(lambda a, b: a + path_sep + b, sys.path)
            # and pass that in to ensure the environment is correct.
            print("Running Testing Script: '" + test_fn + "'")
            subprocess.run(["python", test_fn], env=environment_copy)


def get_files_recursively(r):
    files = []
    for direct, dirnames, filenames in os.walk(r):
        for filename in filenames:
            files.append(os.path.join(direct, filename))
    return files


if __name__ == "__main__":
    main(TEST_DIRS, TEST_EXT, TEST_IGN)
