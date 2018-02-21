# -*- coding: utf-8 -*-
"""
pyserval.client
~~~~~~~~~~~~~~~

This module provides a high-level way to interact with serval
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.lowlevel.keyring import Keyring
from pyserval.lowlevel.rhizome import Rhizome
from pyserval.lowlevel.meshms import MeshMS
from pyserval.lowlevel.meshmb import MeshMB


class ServalClient:
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
        rhizome (rhizome.Rhizome): Provides access to the 'Rhizome'-API, see
                                   https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-Rhizome.md
        meshms (meshms.MeshMS): Provides access to the 'MeshMS'-API, see
                                https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMS.md
        meshmb (meshmb.MeshMB): Provides access to the 'MeshMB'-API, see
                                https://github.com/servalproject/serval-dna/blob/development/doc/REST-API-MeshMB.md
    """
    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self._connection = RestfulConnection(host=host, port=port, user=user, passwd=passwd)
        self.keyring = Keyring(self._connection)
        self.rhizome = Rhizome(self._connection)
        self.meshms = MeshMS(self._connection)
        self.meshmb = MeshMB(self._connection)
