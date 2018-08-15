# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.client
~~~~~~~~~~~~~~~

Collection of API-objects
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.lowlevel.keyring import LowLevelKeyring
from pyserval.lowlevel.rhizome import LowLevelRhizome
from pyserval.lowlevel.meshms import MeshMS
from pyserval.lowlevel.meshmb import MeshMB


class LowLevelClient:
    """Aggregates the low level API-interfaces in one place

    If you do not have a specific reason to use the low-level primitives,
    you should probably go with the high-level client

    Args:
        host (str): Hostname to connect to
        port (int): Port to connect to
        user (str): Username for HTTP basic auth
        passwd (str): Password for HTTP basic auth

    Attributes:
        keyring (keyring.Keyring): Provides access to the 'Keyring'-API, see
                                   https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Keyring.md
        rhizome (rhizome.Rhizome): Provides access to the 'Rhizome'-API, see
                                   https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md
        meshms (meshms.MeshMS): Provides access to the 'MeshMS'-API, see
                                https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMS.md
        meshmb (meshmb.MeshMB): Provides access to the 'MeshMB'-API, see
                                https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMB.md
    """
    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self._connection = RestfulConnection(host=host, port=port, user=user, passwd=passwd)
        self.keyring = LowLevelKeyring(self._connection)
        self.rhizome = LowLevelRhizome(self._connection)
        self.meshms = MeshMS(self._connection)
        self.meshmb = MeshMB(self._connection)
