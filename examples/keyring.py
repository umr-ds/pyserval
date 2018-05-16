#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.highlevel.highlevel_client import HighLevelClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example for keyring-endpoints")
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

    c = HighLevelClient(host=args.host, port=args.port, user=args.user, passwd=args.password)
    keyring = c.keyring

    # Get all identities
    print("Identities:")
    print(keyring.get_identities())

    # Create a new Identity
    new_identity = keyring.add()
    print("New Identity: {}".format(new_identity.sid))

    # Get the identity for a specific SID
    identity_copy = keyring.get_identity(new_identity.sid)

    # Create a new identity, protected with a pin
    # NOTE: We do not save/cache the pin, you are responsible for remembering it
    # FURTHER NOTE: servald does cache pins but you may not want to rely on that...
    new_identity_pin = keyring.add(pin="BatmanIsNotAGoodPassword")
    print("New Identity with PIN: {}".format(new_identity_pin.sid))

    # Create a new identity with both a name and a did
    new_identity_name = keyring.add(name="A Name", did="123456")
    print("New Identity with name and DID: {}".format(new_identity_name))

    # Modify name and did
    modified_identity = keyring.set(new_identity_name, did='11111', name='')
    print("Modified Identity: {}".format(modified_identity))

    # Get a list of 5 identities from the keyring, if there are fewer than 5 unlocked identities available
    # new ones will be created
    five_identities = keyring.get_or_create(5)
    print("5 Identities: {}".format(five_identities))

    # Delete one of the identities
    deleted_identity = keyring.delete(five_identities[0])
    print("Deleted Identity: {}".format(deleted_identity.sid))

    # You can also tell an identity to delete itself
    five_identities[1].delete()
    print("Deleted Itself: {}".format(five_identities[1].sid))

    # Lock an identity
    keyring.lock(five_identities[2])
    print("Locked Identity: {}".format(five_identities[2].sid))

    # Identities can also lock themselves
    five_identities[3].lock()
    print("Locked itself: {}".format(five_identities[3].sid))
