# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.route
~~~~~~~~~~~~~~~~~~~~~~~

This module contains the means to interact with the serval routing-interface
"""

from pyserval.lowlevel.connection import RestfulConnection


class LowLevelRoute:
    """Interface to access routing-related endpoints of the REST-interface

    Args:
        connection (RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection):
        assert isinstance(connection, RestfulConnection)
        self._connection = connection

    def get_all(self):
        """Returns a list of all currently known identities

        Endpoint:
            GET /restful/route/all.json

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get("/restful/route/all.json")
