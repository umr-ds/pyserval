# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.meshms
~~~~~~~~~~~~~~~

This module contains the means to send and receive MeshMS-messages
"""

import sys

# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str


class LowLevelMeshMS:
    """Interface to access MeshMS-related endpoints of the REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection):
        self._connection = connection

    def conversation_list(self, sid):
        """Gets the list of all conversations for a given SID

        Args:
            sid (str): SID of a serval identity

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sid, basestring)
        return self._connection.get(
            "/restful/meshms/{}/conversationlist.json".format(sid)
        )

    def message_list(self, sender, recipient):
        """Gets all the messages sent between two SIDs

        Args:
            sender (str): SID of the message sender
            recipient (str): SID of message recipient

        Note:
            At least one of the SIDs needs to refer to a local unlocken identity in the keyring

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        assert isinstance(sender, basestring)
        assert isinstance(recipient, basestring)
        # TODO: Is this one- or two-way?
        return self._connection.get(
            "/restful/meshms/{}/{}/messagelist.json".format(sender, recipient)
        )

    def message_list_newsince(self, sender, recipient, token):
        """Blocking call, returns first message after provided token, none on timeout.

        Endpoint:
            GET /restful/meshms/SENDERSID/RECIPIENTSID/newsince[/TOKEN]/messagelist.json

        Args:
            sender (str): SID of sending participant
            recipient (str): SID of receiving participant
            token (str): Token denoting the last time the message list was updated
        """
        assert isinstance(sender, basestring)
        assert isinstance(recipient, basestring)
        assert isinstance(token, basestring)
        return self._connection.get(
            "/restful/meshms/{}/{}}/newsince/{}/messagelist.json".format(
                sender, recipient, token
            ),
            stream=True,
        )

    def send_message(
        self, sender, recipient, message, message_type="text/plain", charset="utf-8"
    ):
        """Send a message via MeshMS

        Args:
            sender (str): SID of a local unlocked identity to be used as the sender
            recipient (str): SID of the message recipient
            message (str): content of the message
            message_type (str): MIME-type of the message (default: text/plain)
            charset (str): Character encoding (default: utf-8)
        """
        assert isinstance(sender, basestring)
        assert isinstance(recipient, basestring)
        assert isinstance(message_type, basestring)
        assert isinstance(charset, basestring)

        multipart = [
            (
                "message",
                ("message1", message, "{};charset={}".format(message_type, charset)),
            )
        ]

        self._connection.post(
            "/restful/meshms/{}/{}/sendmessage".format(sender, recipient),
            files=multipart,
        )
