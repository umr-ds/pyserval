# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.client
~~~~~~~~~~~~~~~

Collection of API-objects
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.lowlevel.keyring import LowLevelKeyring
from pyserval.lowlevel.rhizome import LowLevelRhizome
from pyserval.lowlevel.meshms import LowLevelMeshMS
from pyserval.lowlevel.meshmb import LowLevelMeshMB
from pyserval.lowlevel.route import LowLevelRoute


class LowLevelClient:
    """Aggregates the low level API-interfaces in one place

    If you do not have a specific reason to use the low-level primitives,
    you should probably go with the high-level client

    Args:
        connection (RestfulConnection): Connection-object for communication with the REST-endpoints

    Attributes:
        keyring (LowLevelKeyring): Provides access to the 'Keyring'-API, see
                                   https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Keyring.md
        rhizome (LowLevelRhizome): Provides access to the 'Rhizome'-API, see
                                   https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md
        meshms (LowLevelMeshMS): Provides access to the 'MeshMS'-API, see
                                 https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMS.md
        meshmb (LowLevelMeshMB): Provides access to the 'MeshMB'-API, see
                                 https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMB.md
        route (LowLevelRoute): Provides access to the 'Route'-API, see
                               https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Route.md
    """

    def __init__(self, connection):
        assert isinstance(connection, RestfulConnection)
        self._connection = connection
        self.keyring = LowLevelKeyring(self._connection)
        self.rhizome = LowLevelRhizome(self._connection)
        self.meshms = LowLevelMeshMS(self._connection)
        self.meshmb = LowLevelMeshMB(self._connection)
        self.route = LowLevelRoute(self._connection)

    @staticmethod
    def new(host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        """Utility-method that creates a connection-object and then a lient from it

        Args:
            host (str): Hostname to connect to
            port (int): Port to connect to
            user (str): Username for HTTP basic auth
            passwd (str): Password for HTTP basic auth

        Returns:
            LowLevelClient: Fully instantiated client
        """
        connection = RestfulConnection(host=host, port=port, user=user, passwd=passwd)
        return LowLevelClient(connection=connection)
