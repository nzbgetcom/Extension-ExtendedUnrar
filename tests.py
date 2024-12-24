#!/usr/bin/env python3
#
# Copyright (C) 2024-2025 Denis <denis@nzbget.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the program.  If not, see <https://www.gnu.org/licenses/>.
#

import sys
from os.path import dirname
import os
import subprocess
import unittest
import shutil
import json


SUCCESS = 93
NONE = 95
ERROR = 94

unrar = os.environ.get("unrar", "unrar")
unrar_cmd = unrar + " e -idp -ai -o-"

root = dirname(__file__)

test_data_dir = root + "/test_data"
tmp_dir = root + "/tmp"
test_rars = ["test1.rar", "test2.rar", "test3.rar"]
result_files = [tmp_dir + "/test1.txt", tmp_dir + "/test2.txt", tmp_dir + "/test3.txt"]
test_partitioned_rars = ["test4.r01", "test4.r02", "test4.r03"]
test_rars = ["test1.rar", "test2.rar", "test3.rar"]
test_partitioned_result_files = ["test4.bin"]
test_partitioned_result_files = [tmp_dir + "/test4.bin"]

host = "127.0.0.1"
username = "TestUser"
password = "TestPassword"
port = "6789"


def get_python():
    if os.name == "nt":
        return "python"
    return "python3"


def run_script():
    sys.stdout.flush()
    proc = subprocess.Popen(
        [get_python(), root + "/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )
    out, err = proc.communicate()
    proc.pid
    ret_code = proc.returncode
    return (out.decode(), int(ret_code), err.decode())


def set_default_env():
    # NZBGet global options
    os.environ["NZBNA_EVENT"] = "FILE_DOWNLOADED"
    os.environ["NZBPP_DIRECTORY"] = tmp_dir
    os.environ["NZBOP_ARTICLECACHE"] = "8"
    os.environ["NZBPO_PASSACTION"] = "PASSACTION"
    os.environ["NZBOP_CONTROLPORT"] = port
    os.environ["NZBOP_CONTROLIP"] = host
    os.environ["NZBOP_CONTROLUSERNAME"] = username
    os.environ["NZBOP_CONTROLPASSWORD"] = password
    os.environ["NZBPR_PASSWORDDETECTOR_HASPASSWORD"] = "no"
    os.environ["NZBOP_EXTENSIONS"] = ""
    os.environ["NZBOP_UNPACK"] = "yes"
    os.environ["NZBPP_TOTALSTATUS"] = "SUCCESS"

    # script options
    os.environ["NZBNA_CATEGORY"] = "Movies"
    os.environ["NZBNA_DIRECTORY"] = tmp_dir
    os.environ["NZBNA_NZBNAME"] = "TestNZB"
    os.environ["NZBPR_FAKEDETECTOR_SORTED"] = "yes"
    os.environ["NZBOP_TEMPDIR"] = tmp_dir
    os.environ["NZBOP_UNRARCMD"] = unrar_cmd
    os.environ["NZBPO_UNRARCMD"] = unrar_cmd
    os.environ["NZBPO_WAITTIME"] = "0"
    os.environ["NZBPO_DELETELEFTOVER"] = "no"
    os.environ["NZBOP_UNPACKCLEANUPDISK"] = "no"


class Tests(unittest.TestCase):

    def test_unrar(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        set_default_env()

        shutil.copytree(test_data_dir, tmp_dir, dirs_exist_ok=True)

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_unrar_with_empty_unrarcmd_option(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        set_default_env()
        os.environ["NZBPO_UNRARCMD"] = ""

        shutil.copytree(test_data_dir, tmp_dir, dirs_exist_ok=True)

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_multiple_folders(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)
        set_default_env()

        for index, rar in enumerate(test_rars):
            os.mkdir(str(f"{tmp_dir}/{index}"))
            shutil.copyfile(f"{test_data_dir}/{rar}", f"{tmp_dir}/{index}/{rar}")

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in result_files:
            self.assertTrue(os.path.exists(file))

        shutil.rmtree(tmp_dir)

    def test_delete_leftovers(self):
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

        os.mkdir(tmp_dir)
        set_default_env()
        os.environ["NZBPO_DELETELEFTOVER"] = "yes"

        for rar in test_partitioned_rars:
            shutil.copyfile(f"{test_data_dir}/{rar}", f"{tmp_dir}/{rar}")

        [_, code, _] = run_script()

        self.assertEqual(code, SUCCESS)

        for file in test_partitioned_rars:
            self.assertFalse(os.path.exists(file))

        for file in test_partitioned_result_files:
            self.assertTrue(os.path.exists(file))
        shutil.rmtree(tmp_dir)

    def test_manifest(self):
        with open(root + "/manifest.json", encoding="utf-8") as file:
            try:
                json.loads(file.read())
            except ValueError as e:
                self.fail("manifest.json is not valid.")


if __name__ == "__main__":
    unittest.main()
