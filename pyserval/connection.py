# -*- coding: utf-8 -*-
"""
pyserval.connection
~~~~~~~~~~~~~~~~~~~
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.exceptions import UnauthorizedError


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

    def get(self, path, **params):
        """Sends GET-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """

        response = RestfulConnection.get(self, path=path, params=params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def post(self, path, **params):
        """Sends POST-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.post(self, path=path, params=params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def put(self, path, **params):
        """Sends PUT-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.put(self, path=path, params=params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def delete(self, path, **params):
        """Sends DELETE-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.delete(self, path=path, params=params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def patch(self, path, **params):
        """Sends PATCH-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.patch(self, path=path, params=params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response
