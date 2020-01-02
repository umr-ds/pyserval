"""
pyserval.lowlevel.connection
~~~~~~~~~~~~~~~~~~~

This module contains the means to interact directly with the REST-interface
"""

import requests
from typing import Any


class RestfulConnection:
    """Provides the low-level HTTP-capability

    Used by other modules for HTTP-communication

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
        self._AUTH = (user, passwd)
        self._BASE = f"http://{host}:{port}"

    def __repr__(self) -> str:
        return f'RestfulConnection("{self._BASE}")'

    def get(self, path: str, **params: Any) -> requests.models.Response:
        """Sends GET-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (Any): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """

        response = requests.get(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def post(self, path: str, **params: Any) -> requests.models.Response:
        """Sends POST-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (Any): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.post(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def put(self, path: str, **params: Any) -> requests.models.Response:
        """Sends PUT-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (Any): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.put(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def delete(self, path: str, **params: Any) -> requests.models.Response:
        """Sends DELETE-request to REST-API

        Args:
            path (str): (relative) path to the REST-endpoint
            params (Any): Additional parameters to be sent with the request

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        response = requests.delete(self._BASE + path, auth=self._AUTH, **params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    def patch(self, path: str, **params: Any) -> requests.models.Response:
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
