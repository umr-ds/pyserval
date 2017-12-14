"""Tests for pyserval.keyring"""
import os
import random
import shutil
import subprocess

import pytest

from hypothesis import given
from hypothesis.strategies import text, characters, sampled_from, integers

from pyserval.client import ServalClient
from pyserval.keyring import ServalIdentity

names = text(
    characters(blacklist_categories=('Cc', 'Cs')), min_size=1
).map(lambda s: s.strip()).filter(lambda s: len(s.encode("utf-8")) < 64)

dids = text(
    sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9', '#', '0', '*']), min_size=5, max_size=31
)

pins = text(
    characters(blacklist_categories=('Cc', 'Cs'))
)

new_keys = integers(min_value=3, max_value=10)


@pytest.fixture(scope="module")
def serval_init():
    """Test setup/teardown fixture, gets executed once for the module

    Initialises serval and creates connection-object
    """
    # setup
    # create temp-directory
    os.mkdir("/tmp/pyserval-tests/")
    # copy config
    shutil.copy("data/serval.conf", "/tmp/pyserval-tests")
    # set SERVALINSTANCE_PATH
    os.putenv("SERVALINSTANCE_PATH", "/tmp/pyserval-tests/")
    # start servald
    subprocess.call(["servald", "start"])

    yield ServalClient("localhost", port=4110, user="pum", passwd="pum123")

    #teardown
    # stop servald
    subprocess.call(["servald", "stop"])
    # delete temp-directory
    shutil.rmtree("/tmp/pyserval-tests/")


@given(pin=pins)
def test_add(serval_init, pin):
    keyring = serval_init.keyring
    n = len(keyring.get_identities())
    new_identity = keyring.add(pin)
    identities = keyring.get_identities()

    assert len(identities) == n+1
    assert new_identity in identities
    assert keyring.get_identity(new_identity.sid) == new_identity


@given(did=dids, name=names)
def test_set(serval_init, did, name):
    # setup
    keyring = serval_init.keyring
    identities = keyring.get_identities()
    sid = random.choice(identities).sid

    # test local identity
    identity = keyring.set(sid, did, name)
    assert identity.did == did
    assert identity.name == name

    # test remote state
    identity = keyring.get_identity(sid)
    assert identity.did == did
    assert identity.name == name


def test_get_identities(serval_init):
    keyring = serval_init.keyring
    identities = keyring.get_identities()
    assert isinstance(identities, list)

    for identity in identities:
        assert identity is not None
        assert isinstance(identity, ServalIdentity)


def test_get_identity(serval_init):
    keyring = serval_init.keyring
    identities = keyring.get_identities()
    for identity in identities:
        check_identity = keyring.get_identity(identity.sid)
        assert check_identity == identity


def test_remove(serval_init):
    keyring = serval_init.keyring
    identities = keyring.get_identities()
    n = len(identities)
    while n > 0:
        identity = identities[0]
        removed_identity = keyring.remove(identity.sid)
        identities = keyring.get_identities()

        assert removed_identity == identity
        assert len(identities) == n-1
        assert identity not in identities

        n = len(identities)


@given(n=new_keys)
def test_get_or_create(serval_init, n):
    keyring = serval_init.keyring
    identites = keyring.get_or_create(n)
    assert len(identites) == n


def test_lock(serval_init):
    keyring = serval_init.keyring
    identities = keyring.get_identities()
    n = len(identities)
    while n > 0:
        identity = identities[0]
        # FIXME: fails with no identity found
        locked_identity = keyring.lock(identity.sid)
        identities = keyring.get_identities()

        assert locked_identity == identity
        assert len(identities) == n - 1
        assert identity not in identities

        n = len(identities)
