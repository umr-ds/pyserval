#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.client import Client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test rhizome-endpoints")
    parser.add_argument(
        "-ho",
        "--host",
        default="localhost",
        help="Host running the servald REST-interface",
    )
    parser.add_argument(
        "-po", "--port", default=4110, help="Port exposing the servald REST-interface"
    )
    parser.add_argument(
        "-u",
        "--user",
        default="pum",
        help="Username for authentication to the REST interface",
    )
    parser.add_argument(
        "-p",
        "--password",
        default="pum123",
        help="Password for authentication to the REST interface",
    )

    args = parser.parse_args()

    client = Client(
        host=args.host, port=args.port, user=args.user, passwd=args.password
    )
    rhizome = client.rhizome

    # create new bundle with default identity
    new_bundle = rhizome.new_bundle(name="test_default", payload="Batman is no payload")

    # get bundle payload
    print(new_bundle.get_payload())
    print("")

    # change bundle payload
    new_bundle.update_payload("This is a new payload")
    print(new_bundle.payload)
    print("")

    # create new journal
    new_journal = rhizome.new_journal(name="foo", payload="Batman has no journal")

    print(new_journal.get_payload())
    print("")

    # append some payload
    new_journal.append_payload("\nNow he has")
    print(new_journal.payload)
    print("")

    # drop some payload
    # FIXME: buggy endpoint?
    new_journal.drop_payload(21)
    print(new_journal.payload)
    print("")

    # get list of all bundles
    all_bundles = rhizome.get_bundlelist()
    print(all_bundles)
    print("")

    # these bundles don't have their payloads loaded, as this may take some time
    print("Bundle Payload: {}".format(all_bundles[0].payload))
    print("")
    # so you need to call get_payload() once
    all_bundles[0].get_payload()
    print("Bundle Payload: {}".format(all_bundles[0].payload))
    print("")

    # this gets you the bundle for a specific bid
    specific_bundle = rhizome.get_bundle(all_bundles[1].bundle_id)
    # in this case, the payload will already be there
    print(specific_bundle.payload)
    print("")

    # create new bundle with custom manifest fields
    new_bundle_custom = rhizome.new_bundle(
        name="Custom Fields",
        use_default_identity=True,
        custom_manifest={"foo": "bar", "fizz": "buzz"},
    )
    # check custom fields
    bundle_check = rhizome.get_bundle(new_bundle_custom.bundle_id)
    print(bundle_check.manifest.foo)
    print("")
