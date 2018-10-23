#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.client import Client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test MeshMB-endpoints")
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
    meshmb = client.low_level_client.meshmb

    identities = [identity.identity for identity in client.keyring.get_or_create(2)]

    meshmb.send_message(identity=identities[0], message="This is a test broadcast")

    print(meshmb.get_messages(identities[0]))

    meshmb.follow_feed(identities[1], identities[0])
    print(meshmb.get_feedlist(identities[1]))
    print(meshmb.get_activity(identities[1]))
    meshmb.unfollow_feed(identities[1], identities[0])
