"""
pyserval.connection
~~~~~~~~~~~~~~~~~~~
"""

from pyserval.lowlevel.connection import RestfulConnection
from pyserval.exceptions import UnauthorizedError
from typing import Any
from requests.models import Response


class CheckedConnection(RestfulConnection):
    """Encapsulates HTTP-calls and throws exceptions for common error-cases

    Args:
        host (str): Hostname to connect to
        port (int): Port to connect to
        user (str): Username for HTTP basic auth
        passwd (str): Password for HTTP basic auth
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 4110,
        user: str = "pyserval",
        passwd: str = "pyserval",
    ) -> None:
        RestfulConnection.__init__(self, host, port, user, passwd)

    def get(self, path: str, **params: Any) -> Response:
        """Sends GET-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (Any): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """

        response = RestfulConnection.get(self, path, **params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def post(self, path: str, **params: Any) -> Response:
        """Sends POST-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.post(self, path, **params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def put(self, path: str, **params: Any) -> Response:
        """Sends PUT-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.put(self, path, **params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def delete(self, path: str, **params: Any) -> Response:
        """Sends DELETE-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.delete(self, path, **params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response

    def patch(self, path: str, **params: Any) -> Response:
        """Sends PATCH-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (dict[str, Any]): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server

        Throws:
            UnauthorizedError: If username/password is wrong
        """
        response = RestfulConnection.patch(self, path, **params)

        if response.status_code == 401:
            raise UnauthorizedError()

        return response
