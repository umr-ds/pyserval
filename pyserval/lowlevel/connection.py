"""
pyserval.lowlevel.connection
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
        return 'RestfulConnection("{}")'.format(self._BASE)

    def get(self, path, **params):
        """Sends GET-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """

        response = requests.get(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def post(self, path, **params):
        """Sends POST-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.post(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def put(self, path, **params):
        """Sends PUT-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.put(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def delete(self, path, **params):
        """Sends DELETE-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.delete(
            "{}{}".format(self._BASE, path), auth=self._AUTH, **params
        )

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def patch(self, path, **params):
        """Sends PATCH-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.patch(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response
