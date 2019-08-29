#!/usr/bin/env python3

import argparse

from pyserval.client import Client

parser = argparse.ArgumentParser(description="Test MeshMS-endpoints")
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
    "-p",
    "--password",
    default="pum123",
    help="Password for authentication to the REST interface",
)

args = parser.parse_args()

client = Client(host=args.host, port=args.port, user=args.user, passwd=args.password)

meshms = client.meshms

# get first two identites in the keyring
sender, recipient = client.keyring.get_or_create(2)

print("Sending test message\n")
meshms.send_message(
    sender=sender.sid, recipient=recipient.sid, message="This is a test-message"
)

print("Conversation List")
conversations = meshms.conversation_list(sender.sid)
print(conversations)
print()

print("Message List:")
messages = meshms.message_list(sender, recipient)
print(messages)
