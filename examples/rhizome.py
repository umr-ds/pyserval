#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.client import Client


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

    client = Client(host=args.host, port=args.port, user=args.user, passwd=args.password)
    rhizome = client.rhizome

    # create new bundle with default identity
    new_bundle = rhizome.new_bundle(
        name="test_default",
        payload="Batman is no payload",
        use_default_identity=True
    )

    # get bundle payload
    print(new_bundle.get_payload())
    print("")

    # change bundle payload
    new_bundle.update_payload("This is a new payload")
    print(new_bundle.payload)
    print("")

    # create new journal
    new_journal = rhizome.new_journal(
        name="foo",
        payload="Batman has no journal",
        use_default_identity=True
    )

    print(new_journal.get_payload())
    print("")

    # append some payload
    new_journal.append_payload("\nNow he has")
    print(new_journal.payload)
    print("")

    # drop some payload
    new_journal.drop_payload(21)
    print(new_journal.payload)
    print("")
