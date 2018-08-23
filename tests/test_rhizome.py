"""Tests for pyserval.rhizome"""

from pyserval.client import Client
from pyserval.exceptions import DuplicateBundleException
from pyserval.lowlevel.util import autocast

from hypothesis import given
from hypothesis.strategies import text, characters, binary

names = text(characters(blacklist_categories=('Cc', 'Cs')))
payloads = binary()


# if we try to create a bundle which is a 'duplicate' of an existing bundle, it will cause an exception
# to make sure it is expected behaviour, we track all previously created bundles and match in case on an exception
created_bundles = []


@given(name=names, payload=payloads)
def test_new_bundle(serval_init, name, payload):
    """Test adding of new bundles

    Args:
        serval_init (Client): Serval client created by test init
        name (str): Semi-random test names created by hypothesis
        payload (bytes): Random bytes for test payload
    """
    rhizome = serval_init.rhizome
    global created_bundles

    create_parameters = {
        'name': name,
        'payload': payload
    }

    try:
        new_bundle = rhizome.new_bundle(
            name=name,
            payload=payload
        )
    except DuplicateBundleException:
        # check, if we actually already created this bundle
        assert create_parameters in created_bundles
        return

    created_bundles.append(create_parameters)

    test_bundle = rhizome.get_bundle(new_bundle.bundle_id)

    # as it turns out, if no name is provided, serval will will set it to "file1"
    if not name:
        assert test_bundle.manifest.name == "file1"
    else:
        # manifest fields are automatically cast into their respective data types if they
        # are merely string representations
        assert test_bundle.manifest.name == autocast(name)

    assert test_bundle.get_payload() == payload
