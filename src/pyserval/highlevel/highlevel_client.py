# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.client
~~~~~~~~~~~~~~~

This module provides a high-level way to interact with serval
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.highlevel.highlevel_keyring import HighLevelKeyring


class HighLevelClient:
    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self._connection = RestfulConnection(host=host, port=port, user=user, passwd=passwd)
        self.keyring = HighLevelKeyring(self._connection)
