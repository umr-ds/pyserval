# -*- coding: utf-8 -*-
"""
pyserval.client
~~~~~~~~~~~~~~~

This module provides a high-level way to interact with serval
"""

from pyserval.lowlevel.client import LowLevelClient
from pyserval.connection import CheckedConnection
from pyserval.keyring import Keyring
from pyserval.rhizome import Rhizome
from pyserval.meshms import MeshMS
from pyserval.meshmb import MeshMB
from pyserval.route import Route


class Client:
    """Meta-Class to access package functionality

        Allows for the automatic initialisation of all API-objects at once.

        Args:
            host (str): Hostname to connect to
            port (int): Port to connect to
            user (str): Username for HTTP basic auth
            passwd (str): Password for HTTP basic auth

        Attributes:
            keyring (Keyring): Provides access to the 'Keyring'-API, see
                               https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Keyring.md
            rhizome (Rhizome): Provides access to the 'Rhizome'-API, see
                               https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md
            meshms (MeshMS): Provides access to the 'MeshMS'-API, see
                             https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMS.md
            meshmb (MeshMB): Provides access to the 'MeshMB'-API, see
                             https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMB.md
            route (Route): Provides access to the 'Route'-API, see
                           https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Route.md
        """

    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self._connection = CheckedConnection(
            host=host, port=port, user=user, passwd=passwd
        )
        self._low_level_client = LowLevelClient(self._connection)
        self.keyring = Keyring(self._low_level_client.keyring)
        self.rhizome = Rhizome(self._low_level_client.rhizome, self.keyring)
        self.meshms = MeshMS(self._low_level_client.meshms)
        self.meshmb = MeshMB(self._low_level_client.meshmb)
        self.route = Route(self._low_level_client.route)
