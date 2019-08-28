#!/usr/bin/env python3

import argparse

from pyserval.client import Client

parser = argparse.ArgumentParser(description="Example for route-endpoints")
parser.add_argument(
    "-ho", "--host", default="localhost", help="Host running the servald REST-interface"
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
    "-pw",
    "--password",
    default="pum123",
    help="Password for authentication to the REST interface",
)

args = parser.parse_args()

c = Client(host=args.host, port=args.port, user=args.user, passwd=args.password)
route = c.route
print(route.get_all())
