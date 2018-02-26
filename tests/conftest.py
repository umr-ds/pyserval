"""Initialisation of the test-enviroment"""

import os
import shutil
import subprocess

import pytest

from pyserval.lowlevel.client import ServalClient
from pyserval.highlevel.highlevel_client import HighLevelClient


@pytest.fixture(scope="module")
def serval_init():
    """Test setup/teardown fixture, gets executed once for the module

    Initialises serval and creates connection-object
    """
    # setup
    # create temp-directory
    os.mkdir("/tmp/pyserval-tests/")
    # copy config
    shutil.copy("tests/data/serval.conf", "/tmp/pyserval-tests")
    # set SERVALINSTANCE_PATH
    os.putenv("SERVALINSTANCE_PATH", "/tmp/pyserval-tests/")
    # start servald
    subprocess.call(["servald", "start"])

    low_level_client = ServalClient("localhost", port=4110, user="pum", passwd="pum123")
    high_level_client = HighLevelClient("localhost", port=4110, user="pum", passwd="pum123")

    yield low_level_client, high_level_client

    # teardown
    # stop servald
    subprocess.call(["servald", "stop"])
    # delete temp-directory
    shutil.rmtree("/tmp/pyserval-tests/")
