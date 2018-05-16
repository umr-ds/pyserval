#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.lowlevel.client import LowLevelClient
from pyserval.lowlevel.rhizome import Manifest
from pyserval.lowlevel.util import generate_secret


def anonymous_journal(cli):
    """Creates an anonymous journal (bundle_author not set) with some payload

    Note that with journals, when you set and update the payload, the new payload will be appended.

    Also note that with anonymous bundles/journals, you need to store the bundle_secret.
    Otherwise you will be unable to modify the bundle later
    """
    manifest = Manifest(name="test-journal", service="testservice", tail=0)
    journal = cli.rhizome.append(manifest=manifest,
                                 bundle_secret=generate_secret(),
                                 payload="This is a test\n")
    journal.payload = "Some more tests\n"
    journal.update()
    return journal


def bundle_with_author(cli):
    """Creates a bundle with a local identity as author

    This way, the bundle can be updated later, even if the bundle_secret is not stored
    """

    # first, we need to get an identity
    identity = cli.keyring.get_or_create(1)[0]

    manifest = Manifest(name="test-bundle", service="testservice")
    bundle = cli.rhizome.insert(manifest=manifest,
                                bundle_author=identity.sid,
                                payload="This is a test\n")
    return bundle


def bundle_with_custom_field(cli):
    """Creates a bundle with a custom field in its manifest"""

    # first, we need to get an identity
    identity = cli.keyring.get_or_create(1)[0]

    manifest = Manifest(name="custom-field", service="testservice", custom="foo", custom2="bar")
    bundle = cli.rhizome.insert(manifest=manifest,
                                bundle_author=identity.sid,
                                payload="Bundle with a custom field\n")
    return bundle


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test rhizome-endpoints")
    parser.add_argument('-ho',
                        '--host',
                        default='localhost',
                        help='Host running the servald REST-interface')
    parser.add_argument('-po',
                        '--port',
                        default=4110,
                        help='Port exposing the servald REST-interface')
    parser.add_argument('-u',
                        '--user',
                        default='pum',
                        help='Username for authentication to the REST interface')
    parser.add_argument('-p',
                        '--password',
                        default='pum123',
                        help='Password for authentication to the REST interface')

    args = parser.parse_args()

    c = LowLevelClient(host=args.host, port=args.port, user=args.user, passwd=args.password)

    journal = anonymous_journal(c)
    bundle = bundle_with_author(c)
    custom_bundle = bundle_with_custom_field(c)

    # List all bundles in the rhizome store
    bundles = c.rhizome.get_bundlelist()
    print("Bundles:")
    print(bundles)
    print()

    # get the manifest of the first bundle in the store
    manifest = c.rhizome.get_manifest(bundles[0].bundle_id)
    print("Manifest:")
    print(manifest)
    print()

    # get the payload of the first bundle in the store
    data = c.rhizome.get_raw(bundles[0].manifest.id)
    print("Payload:")
    print(data)
    print()
