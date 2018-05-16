# -*- coding: utf-8 -*-
"""
pyserval.connection
~~~~~~~~~~~~~~~~~~~

This module contains the means to interact directly with the REST-interface
"""

import requests


class RestfulConnection:
    """Provides the low-level HTTP-capability

    Used by other modules for HTTP-communication

    Args:
        host (str): Hostname to connect to
        port (int): Port to connect to
        user (str): Username for HTTP basic auth
        passwd (str): Password for HTTP basic auth
    """
    def __init__(self, host="localhost", port=4110, user="pyserval", passwd="pyserval"):
        self._AUTH = (user, passwd)
        self._BASE = "http://{}:{}".format(host, port)

    def __repr__(self):
        return "RestfulConnection(\"{}\")".format(self._BASE)

    def get(self, path, **params):
        """Sends GET-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        request = requests.get(self._BASE + path, auth=self._AUTH, **params)
        return request

    def post(self, path, **params):
        """Sends POST-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        request = requests.post(self._BASE + path, auth=self._AUTH, **params)
        return request
