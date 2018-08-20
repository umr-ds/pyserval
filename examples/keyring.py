#!/usr/bin/env python
from __future__ import print_function

import argparse

from pyserval.client import Client

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

    c = Client(host=args.host, port=args.port, user=args.user, passwd=args.password)
    keyring = c.keyring

    # Get all identities
    print("Identities:")
    print(keyring.get_identities())

    # If you don't care about the exact identity, you can just get a default one
    # NOTE: if there are no unlocked identities in your keyring, a new one will be created
    default_identity = keyring.default_identity()
    print("Default identity: {}".format(default_identity))

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
    modified_identity = keyring.set(new_identity_name, did="654321", name="Another Name")
    print("Modified Identity: {}".format(modified_identity))

    # Reset name & did back to empty string
    reset_identity = keyring.reset(identity=modified_identity, did=True, name=True)
    print("Reset Identity: {}".format(reset_identity))

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
    locked_identity = keyring.lock(five_identities[2])
    print("Locked Identity: {}".format(locked_identity.sid))

    # Identities can also lock themselves
    five_identities[3].lock()
    print("Locked itself: {}".format(five_identities[3].sid))

    # The ServalIdentity-Class has a number of convenient auxilliary methods
    # If you want to be sure that your local state is not stale, you can have an identity refresh its information

    refreshed_identity = keyring.default_identity()
    keyring.set(identity=refreshed_identity, name="Will be refreshed")
    refreshed_identity.refresh()
    print("Refreshed identity: {}".format(refreshed_identity))
