"""Tests for pyserval.rhizome"""

from pyserval.client import Client

from hypothesis import given
from hypothesis.strategies import text, characters

names = text(characters(blacklist_categories=('Cc', 'Cs')))


@given(name=names)
def test_new_bundle(serval_init, name):
    """Test adding of new bundles

    Args:
        serval_init (Client): Serval client created by test init
        name (str): Semi-random test names created by hypothesis
    """
    rhizome = serval_init.rhizome

    new_bundle = rhizome.new_bundle(
        name=name,
        use_default_identity=True
    )

    test_bundle = rhizome.get_bundle(new_bundle.bundle_id)

    # as it turns out, if no name is provided, serval will will set it to "file1"
    if not name:
        assert test_bundle.manifest.name == "file1"
    else:
        # manifest fields are automatically cast into their respective data types if they
        # are merely string representations
        assert str(test_bundle.manifest.name) == name
