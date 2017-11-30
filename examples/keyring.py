#!/usr/bin/env python3
from __future__ import print_function

import argparse

from pyserval.client import ServalClient

parser = argparse.ArgumentParser(description="Test keyring-endpoints")
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
parser.add_argument('-pw',
                    '--password',
                    default='pum123',
                    help='Password for authentication to the REST interface')

args = parser.parse_args()

c = ServalClient(host=args.host, port=args.port, user=args.user, passwd=args.password)

print("Identities:")
print(c.keyring.get_identities())
