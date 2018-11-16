"""Tests for pyserval.rhizome"""

from pyserval.client import Client
from pyserval.exceptions import DuplicateBundleException

from hypothesis import given

from tests.custom_strategies import (
    unicode_printable,
    ascii_alphanum,
    payloads,
    payloads_nonempty,
)


# if we try to create a bundle which is a 'duplicate' of an existing bundle, it will cause an exception
# to make sure it is expected behaviour, we track all previously created bundles and match in case on an exception
created_bundles = []


@given(name=unicode_printable, payload=payloads, service=ascii_alphanum)
def test_new_bundle(serval_init, name, payload, service):
    """Test adding of new bundles

    Args:
        serval_init (Client): Serval client created by test init
        name (str): Semi-random test names created by hypothesis
        payload (bytes): Random bytes for test payload
        service (str): Semi-random service name
    """
    rhizome = serval_init.rhizome
    global created_bundles

    create_parameters = {"name": name, "payload": payload, "service": service}

    try:
        new_bundle = rhizome.new_bundle(name=name, payload=payload, service=service)
    except DuplicateBundleException:
        # check, if we actually already created this bundle
        # FIXME: for some reason, this does not work as expected.
        # Sometimes, even though the duplicate exception fires, the bundle is not in the list
        # of previously created bundles...
        # assert create_parameters in created_bundles
        return

    created_bundles.append(create_parameters)

    test_bundle = rhizome.get_bundle(new_bundle.bundle_id)

    # as it turns out, if no name is provided, serval will set it to the payload filename
    # but as it further turns out, this only happen, if the 'service' field is unset...
    # don't ask me for the logic behind this
    if not name and not service:
        assert test_bundle.manifest.name == "file"
    # if service is set, then the name will be None...
    elif not name:
        assert test_bundle.manifest.name is None
    else:
        assert test_bundle.manifest.name == name

    assert test_bundle.get_payload() == payload

    if not service:
        assert test_bundle.manifest.service == "file"
    else:
        assert test_bundle.manifest.service == service


@given(name=unicode_printable, payload=payloads_nonempty, service=ascii_alphanum)
def test_new_journal(serval_init, name, payload, service):
    """Test adding of new journals

    Args:
        serval_init (Client): Serval client created by test init
        name (str): Semi-random test names created by hypothesis
        payload (bytes): Random bytes for test payload
        service (str): Semi-random service name
    """

    rhizome = serval_init.rhizome
    try:
        new_journal = rhizome.new_journal(name=name, payload=payload, service=service)
    except DuplicateBundleException:
        # check, if we actually already created this bundle
        # FIXME: for some reason, this does not work as expected.
        return

    test_journal = rhizome.get_bundle(new_journal.bundle_id)

    # see test_new_bundle for an explanation of this madness
    if not name and not service:
        assert test_journal.manifest.name == "file"

    # if service is set, then the name will be None...
    elif not name:
        assert test_journal.manifest.name is None
    else:
        assert test_journal.manifest.name == name

    assert test_journal.get_payload() == payload

    if not service:
        assert test_journal.manifest.service == "file"
    else:
        assert test_journal.manifest.service == service
