# -*- coding: utf-8 -*-
"""
pyserval.connection
~~~~~~~~~~~~~~~~~~~
"""

from pyserval.lowlevel.connection import RestfulConnection


class CheckedConnection(RestfulConnection):
    """Encapsulates HTTP-calls and throws exceptions for common error-cases

    Args:
        host (str): Hostname to connect to
        port (int): Port to connect to
        user (str): Username for HTTP basic auth
        passwd (str): Password for HTTP basic auth
    """

    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        RestfulConnection.__init__(self, host, port, user, passwd)
