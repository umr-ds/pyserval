# -*- coding: utf-8 -*-
"""
pyserval.meshms
~~~~~~~~~~~~~~~

This module contains the means to send and receive MeshMS-messages
"""

from pyserval.util import unmarshall


class Message:
    """Representation of a MeshMS message

    Args:
        type (str): Was the message sent ('>'), or received ('<')
        my_sid (str): SID of the sender (?)
        their_sid (str): SID of the recipient (?)
        my_offset (int): Offset of the sender (?)
        their_offset (int): Offset of the recipient (?)
        token (str): Token for real-time access (not implemented)
        text (str): Content of the message
        delivered (bool): Whether the message has been successfully delivered
        read (bool): Whether the recipient has read the message
        timestamp (int): UNIX-timestamp of when the message was sent
        ack_offset (int): (?)

    Attributes:
        type (str): Was the message sent ('>'), or received ('<')
        my_sid (str): SID of the sender (?)
        their_sid (str): SID of the recipient (?)
        my_offset (int): Offset of the sender (?)
        their_offset (int): Offset of the recipient (?)
        token (str): Token for real-time access (not implemented)
        text (str): Content of the message
        delivered (bool): Whether the message has been successfully delivered
        read (bool): Whether the recipient has read the message
        timestamp (int): UNIX-timestamp of when the message was sent
        ack_offset (int): (?)
    """
    # TODO: Find the exact menaing of 'my' and 'their'
    def __init__(self,
                 type,
                 my_sid,
                 their_sid,
                 my_offset,
                 their_offset,
                 token,
                 text,
                 delivered,
                 read,
                 timestamp,
                 ack_offset):
        self.type = type
        self.my_sid = my_sid
        self.their_sid = their_sid
        self.my_offset= my_offset
        self.their_offset = their_offset
        self.token = token
        self.text = text
        self.delivered = delivered
        self.read = read
        self.timestamp = timestamp
        self.ack_offset = ack_offset

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class Conversation:
    """Representation of a MeshMS conversation

    Args:
        _id (str): IF of the conversation (?)
        my_sid (str): SID of the sender (?)
        their_sid (str): SID of the recipient (?)
        read (bool): Whether the latest message has been read (?)
        last_message (str): Content of the latest message (?)
        read_offset (int): Offset of the latest read message (?)

    Attributes:
        my_sid (str): SID of the sender (?)
        their_sid (str): SID of the recipient (?)
        read (bool): Whether the latest message has been read (?)
        last_message (str): Content of the latest message (?)
        read_offset (int): Offset of the latest read message (?)

    """
    def __init__(self,
                 _id,
                 my_sid,
                 their_sid,
                 read,
                 last_message,
                 read_offset):
        self._id = _id
        self.my_sid = my_sid
        self.their_sid = their_sid
        self.read = read
        self.last_message = last_message
        self.read_offset = read_offset

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class MeshMS:
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
            List[Conversation]: List of all the conversations
                                that the specified identity is taking part in
        """
        result = self._connection.get("/restful/meshms/{}/conversationlist.json".format(sid)).json()
        conversations = unmarshall(json_table=result, object_class=Conversation)
        return conversations

    def message_list(self, sender, recipient):
        """Gets all the messages sent between two SIDs

        Args:
            sender (str): SID of the message sender
            recipient (str): SID of message recipient

        Note:
            At least one of the SIDs needs to refer to a local unlocken identity in the keyring

        Returns:
            List[Message]: List of all the messages sent between the two identitites
        """
        # TODO: Is this one- or two-way?
        result = self._connection.get(
            "/restful/meshms/{}/{}/messagelist.json".format(sender, recipient)
        ).json()

        messages = unmarshall(json_table=result, object_class=Message)
        return messages

    def send_message(self,
                     sender,
                     recipient,
                     message,
                     message_type="text/plain",
                     charset="utf-8"):
        """Send a message via MeshMS

        Args:
            sender (str): SID of a local unlocked identity to be used as the sender
            recipient (str): SID of the message recipient
            message (str): content of the message
            message_type (str): MIME-type of the message (default: text/plain)
            charset (str): Character encoding (default: utf-8)
        """
        multipart = [
            (
                "message",
                ("message1", message, "{};charset={}".format(message_type, charset))
            )
        ]

        self._connection.post(
            "/restful/meshms/{}/{}/sendmessage".format(sender, recipient),
            files=multipart
        )
