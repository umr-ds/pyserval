"""Tests for pyserval.highlevel.highlevel_keyring"""
import random

from hypothesis import given
from hypothesis.strategies import text, characters, sampled_from, integers, booleans

from pyserval.highlevel.keyring import ServalIdentity

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

bools = booleans()


@given(pin=pins)
def test_add(serval_init, pin):
    keyring = serval_init[1].keyring
    n = len(keyring.get_identities())
    new_identity = keyring.add(pin)
    identities = keyring.get_identities()

    assert len(identities) == n+1
    assert new_identity in identities
    assert keyring.get_identity(new_identity.sid) == new_identity


@given(did=dids, name=names)
def test_set(serval_init, did, name):
    # setup
    keyring = serval_init[1].keyring
    identities = keyring.get_identities()
    random_identity = random.choice(identities)

    # test local identity
    identity = keyring.set(random_identity, did=did, name=name)
    # if name or did is emptystring, it is not changed
    if did:
        assert identity.did == did
    else:
        assert identity.did == random_identity.did

    if name:
        assert identity.name == name
    else:
        assert identity.name == random_identity.name

    # test remote state
    identity = keyring.get_identity(random_identity.sid)
    if did:
        assert identity.did == did
    else:
        assert identity.did == random_identity.did

    if name:
        assert identity.name == name
    else:
        assert identity.name == random_identity.name


@given(did=bools, name=bools)
def test_reset(serval_init, did, name):
    # setup
    keyring = serval_init[1].keyring
    identities = keyring.get_identities()
    random_identity = random.choice(identities)

    identity = keyring.reset(identity=random_identity, name=name, did=did)
    remote_identity = keyring.get_identity(sid=random_identity.sid)

    if did:
        assert identity.did == ""
        assert remote_identity.did == ""
    else:
        assert identity.did == random_identity.did
        assert remote_identity.did == random_identity.did

    if name:
        assert identity.name == ""
        assert remote_identity.name == ""
    else:
        assert identity.name == random_identity.name
        assert remote_identity.name == random_identity.name


def test_get_identities(serval_init):
    keyring = serval_init[1].keyring
    identities = keyring.get_identities()
    assert isinstance(identities, list)

    for identity in identities:
        assert identity is not None
        assert isinstance(identity, ServalIdentity)


def test_get_identity(serval_init):
    keyring = serval_init[1].keyring
    identities = keyring.get_identities()
    for identity in identities:
        check_identity = keyring.get_identity(identity.sid)
        assert check_identity == identity


def test_remove(serval_init):
    keyring = serval_init[1].keyring
    identities = keyring.get_identities()
    n = len(identities)
    while n > 0:
        identity = identities[0]
        removed_identity = keyring.delete(identity)
        identities = keyring.get_identities()

        assert removed_identity == identity
        assert len(identities) == n-1
        assert identity not in identities

        n = len(identities)


@given(n=new_keys)
def test_get_or_create(serval_init, n):
    keyring = serval_init[1].keyring
    identites = keyring.get_or_create(n)
    assert len(identites) == n


@given(did=dids, name=names)
def test_identity_refresh(serval_init, did, name):
    """Test the 'refresh' method of the ServalIdentity Class"""
    keyring = serval_init[1].keyring
    identities = keyring.get_identities()
    random_identity = random.choice(identities)

    # set name & did to new values
    keyring.set(identity=random_identity, did=did, name=name)

    # refresh identity
    random_identity.refresh()

    # check if new local state is valid
    if did:
        assert random_identity.did == did
    if name:
        assert random_identity.name == name
