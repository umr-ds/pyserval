"""Initialisation of the test-enviroment"""

import os
import shutil
import subprocess

import pytest

from pyserval.lowlevel.client import LowLevelClient
from pyserval.client import Client


serval_conf = "interfaces.0.match=lo\napi.restful.users.pum.password=pum123\n"


@pytest.fixture(scope="module")
def serval_init():
    """Test setup/teardown fixture, gets executed once for the module

    Initialises serval and creates connection-object
    """
    # setup
    # create temp-directory
    os.mkdir("/tmp/pyserval-tests/")

    # write config
    with open("/tmp/pyserval-tests/serval.conf", "w+") as f:
        f.write(serval_conf)

    # set SERVALINSTANCE_PATH
    os.putenv("SERVALINSTANCE_PATH", "/tmp/pyserval-tests/")

    # start servald
    subprocess.call(["servald", "start"])

    low_level_client = LowLevelClient("localhost", port=4110, user="pum", passwd="pum123")
    high_level_client = Client("localhost", port=4110, user="pum", passwd="pum123")

    yield low_level_client, high_level_client

    # teardown
    # stop servald
    subprocess.call(["servald", "stop"])

    # delete temp-directory
    shutil.rmtree("/tmp/pyserval-tests/")
