# -*- coding: utf-8 -*-
"""
pyserval.client
~~~~~~~~~~~~~~~

This module provides a high-level way to interact with serval
"""

from pyserval.lowlevel.client import LowLevelClient
from pyserval.keyring import Keyring
from pyserval.rhizome import Rhizome
from pyserval.meshms import MeshMS
from pyserval.meshmb import MeshMB


class Client:
    """Meta-Class to access package functionality

        Allows for the automatic initialisation of all API-objects at once.

        Args:
            host (str): Hostname to connect to
            port (int): Port to connect to
            user (str): Username for HTTP basic auth
            passwd (str): Password for HTTP basic auth

        Attributes:
            keyring (keyring.Keyring): Provides access to the 'Keyring'-API, see
                                       https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Keyring.md
        """

    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self.low_level_client = LowLevelClient(
            host=host, port=port, user=user, passwd=passwd
        )
        self.keyring = Keyring(self.low_level_client.keyring)
        self.rhizome = Rhizome(self.low_level_client.rhizome, self.keyring)
        self.meshms = MeshMS(self.low_level_client.meshms)
        self.meshmb = MeshMB(self.low_level_client.meshmb)
