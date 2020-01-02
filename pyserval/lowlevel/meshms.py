"""
pyserval.lowlevel.meshms
~~~~~~~~~~~~~~~

This module contains the means to send and receive MeshMS-messages
"""

from pyserval.connection import RestfulConnection
from requests.models import Response


class LowLevelMeshMS:
    """Interface to access MeshMS-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection: RestfulConnection) -> None:
        assert isinstance(connection, RestfulConnection)
        self._connection = connection

    def conversation_list(self, sid: str) -> Response:
        """Gets the list of all conversations for a given SID

        Args:
            sid (str): SID of a serval identity

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, str)
        return self._connection.get(f"/restful/meshms/{sid}/conversationlist.json")

    def message_list(self, sender: str, recipient: str) -> Response:
        """Gets all the messages sent between two SIDs

        Args:
            sender (str): SID of the message sender
            recipient (str): SID of message recipient

        Note:
            At least one of the SIDs needs to refer to a local unlocken identity in the keyring

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sender, str)
        assert isinstance(recipient, str)
        # TODO: Is this one- or two-way?
        return self._connection.get(
            f"/restful/meshms/{sender}/{recipient}/messagelist.json"
        )

    def message_list_newsince(
        self, sender: str, recipient: str, token: str
    ) -> Response:
        """Blocking call, returns first message after provided token, none on timeout.

        Endpoint:
            GET /restful/meshms/SENDERSID/RECIPIENTSID/newsince[/TOKEN]/messagelist.json

        Args:
            sender (str): SID of sending participant
            recipient (str): SID of receiving participant
            token (str): Token denoting the last time the message list was updated
        """
        assert isinstance(sender, str)
        assert isinstance(recipient, str)
        assert isinstance(token, str)
        return self._connection.get(
            f"/restful/meshms/{sender}/{recipient}/newsince/{token}/messagelist.json",
            stream=True,
        )

    def send_message(
        self,
        sender: str,
        recipient: str,
        message: str,
        message_type: str = "text/plain",
        charset: str = "utf-8",
    ) -> Response:
        """Send a message via MeshMS

        Args:
            sender (str): SID of a local unlocked identity to be used as the sender
            recipient (str): SID of the message recipient
            message (str): content of the message
            message_type (str): MIME-type of the message (default: text/plain)
            charset (str): Character encoding (default: utf-8)
        """
        assert isinstance(sender, str)
        assert isinstance(recipient, str)
        assert isinstance(message_type, str)
        assert isinstance(charset, str)

        multipart = [
            ("message", ("message1", message, f"{message_type};charset={charset}"),)
        ]

        return self._connection.post(
            f"/restful/meshms/{sender}/{recipient}/sendmessage", files=multipart,
        )
