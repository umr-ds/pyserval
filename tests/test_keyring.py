import random

from hypothesis import given
from hypothesis.strategies import text, characters, sampled_from, integers

from pyserval.client import ServalClient
from pyserval.keyring import ServalIdentity

names = text(
    characters(blacklist_categories=('Cc', 'Cs')), min_size=1
).map(lambda s: s.strip()).filter(lambda s: len(bytes(s, "utf-8")) < 64)

dids = text(
    sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9', '#', '0', '*']), min_size=5, max_size=31
)

pins = text(
    characters(blacklist_categories=('Cc', 'Cs'))
)

new_keys = integers(min_value=3, max_value=10)


keyring = ServalClient("localhost", port=4110, user="pum", passwd="pum123").keyring


@given(pins)
def test_add(pin):
    n = len(keyring.get_identities())
    new_identity = keyring.add(pin)
    identities = keyring.get_identities()

    assert len(identities) == n+1
    assert new_identity in identities
    assert keyring.get_identity(new_identity.sid) == new_identity


@given(dids, names)
def test_set(did, name):
    # setup
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


def test_get_identities():
    identities = keyring.get_identities()
    assert isinstance(identities, list)

    for identity in identities:
        assert identity is not None
        assert isinstance(identity, ServalIdentity)


def test_get_identity():
    identities = keyring.get_identities()
    for identity in identities:
        check_identity = keyring.get_identity(identity.sid)
        assert check_identity == identity


def test_remove():
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


@given(new_keys)
def test_get_or_create(n):
    identites = keyring.get_or_create(n)
    assert len(identites) == n


def test_lock():
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
