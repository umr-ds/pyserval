# -*- coding: utf-8 -*-
"""
pyserval.client
~~~~~~~~~~~~~~~

This module provides a high-level way to interact with serval
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.keyring import Keyring


class Client:
    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self._connection = RestfulConnection(host=host, port=port, user=user, passwd=passwd)
        self.keyring = Keyring(self._connection)
