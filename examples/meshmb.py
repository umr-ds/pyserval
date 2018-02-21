#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.lowlevel.client import ServalClient


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test MeshMB-endpoints")
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

    client = ServalClient(host=args.host, port=args.port, user=args.user, passwd=args.password)

    identities = [identity.identity for identity in client.keyring.get_or_create(2)]

    client.meshmb.send_message(identity=identities[0],
                               message="This is a test broadcast")

    print(client.meshmb.get_messages(identities[0]))

    client.meshmb.follow_feed(identities[1], identities[0])
    print(client.meshmb.get_feedlist(identities[1]))
    print(client.meshmb.get_activity(identities[1]))
    client.meshmb.unfollow_feed(identities[1], identities[0])
