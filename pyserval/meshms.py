# -*- coding: utf-8 -*-
"""
pyserval.meshms
~~~~~~~~~~~~~~~~

High level interface for meshms-messaging
"""

import sys
import json

from pyserval.lowlevel.util import unmarshall
from pyserval.lowlevel.meshms import LowLevelMeshMS
from pyserval.keyring import ServalIdentity
from pyserval.exceptions import (
    ConversationNotFoundError,
    InvalidTokenError,
    RhizomeHTTPStatusError,
)

# python3 does not have the basestring type, since it does not have the unicode type
# if we are running under python3, we just test for str
if sys.version_info >= (3, 0, 0):
    basestring = str

MESSAGELIST_HEADER_SIZE = 178
MESSAGELIST_HEADER_NEWLINES = 5


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
        type (str): Was the message sent ('>'), or received ('<'), or ACK
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
    def __init__(
        self,
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
        ack_offset,
    ):
        self.type = type
        self.my_sid = my_sid
        self.their_sid = their_sid
        self.my_offset = my_offset
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
        _meshms (MeshMS): Interface for future Interactions
        messages (List[Message]): Messages associated with this conversation

    """

    def __init__(self, _id, my_sid, their_sid, read, last_message, read_offset):
        self._id = _id
        self.my_sid = my_sid
        self.their_sid = their_sid
        self.read = read
        self.last_message = last_message
        self.read_offset = read_offset
        self._meshms = None
        self.messages = []

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def get_messages(self):
        """Update the message list"""
        self.messages = self._meshms.message_list(
            sender=self.my_sid, recipient=self.their_sid
        )

    def received_messages(self):
        """Returns all messages received by this identity in this conversation"""
        self.get_messages()
        received = [message for message in self.messages if message.type == "<"]
        return received

    def sent_messages(self):
        """Returns all messages sent by this identity in this conversation"""
        self.get_messages()
        sent = [message for message in self.messages if message.type == ">"]
        return sent

    def unread(self):
        """Returns all received messages which have not been read yet"""
        # FIXME: serval seems to never update the 'read' field,
        #        even if there exists an ACK and the messages have been queried...
        received = self.received_messages()
        unread = [message for message in received if not message.read]
        return unread

    def send_message(self, message):
        """Sends a message to them

        Args:
            message (basestring)
        """
        self._meshms.send_message(
            sender=self.my_sid, recipient=self.their_sid, message=message
        )


class MeshMS:
    """Interface to send & receive meshms-messages

    Args:
        low_level (LowLevelMeshMS): Interface for low level operations
    """

    def __init__(self, low_level):
        self._low_level = low_level

    def conversation_list(self, identity):
        """Gets the list of all conversations for a given Identity

        Args:
            identity (Union[ServalIdentity, str])

        Returns:
            List[Conversation]: List of all the conversations
                                that the specified identity is taking part in
        """
        if isinstance(identity, ServalIdentity):
            identity = identity.sid

        assert isinstance(
            identity, basestring
        ), "identity has to be either a string or ServalIdentity"

        result = self._low_level.conversation_list(identity)

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)

        conversations = unmarshall(json_table=result.json(), object_class=Conversation)
        for conversation in conversations:
            conversation._meshms = self
        return conversations

    def get_conversation(self, identity, other_identity):
        """Gets the conversation between the two identities, if it exists

        Args:
            identity (Union[ServalIdentity, str])
            other_identity (Union[ServalIdentity, str])

        Returns:
            Conversation

        Raises:
            ConversationNotFoundError: If no conversation between the two SIDs exists
        """
        if isinstance(identity, ServalIdentity):
            identity = identity.sid
        if isinstance(other_identity, ServalIdentity):
            other_identity = other_identity.sid

        assert isinstance(
            identity, basestring
        ), "identity has to be either a string or ServalIdentity"
        assert isinstance(
            other_identity, basestring
        ), "other_identity has to be either a string or ServalIdentity"

        conversations = self.conversation_list(identity)
        for conversation in conversations:
            if conversation.their_sid == other_identity:
                return conversation

        raise ConversationNotFoundError(sid=identity, other_sid=other_identity)

    def message_list(self, sender, recipient):
        """Gets all the messages sent between two identities

        Args:
            sender (ServalIdentity)
            recipient (ServalIdentity)

        Note:
            At least one of the identities needs to be local and unlocked

        Returns:
            List[Message]: List of all the messages sent between the two identities
        """
        assert isinstance(sender, ServalIdentity)
        assert isinstance(recipient, ServalIdentity)

        # TODO: Is this one- or two-way?
        result = self._low_level.message_list(
            sender=sender.sid, recipient=recipient.sid
        )

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)

        result_json = result.json()
        messages = unmarshall(json_table=result_json, object_class=Message)
        return messages

    def message_list_newsince(self, sender, recipient, token):
        """Gets all the messages sent between two identities since the token was generated

        Args:
            sender (ServalIdentity)
            recipient (ServalIdentity)
            token (str)

        Note:
            At least one of the identities needs to be local and unlocked

        Returns:
            List[Message]: List of all the messages sent between the two identities
        """
        assert isinstance(sender, ServalIdentity)
        assert isinstance(recipient, ServalIdentity)
        assert isinstance(token, basestring)

        with self._low_level.message_list_newsince(
            sender=sender.sid, recipient=recipient.sid, token=token
        ) as serval_stream:

            if serval_stream.status_code == 404:
                raise InvalidTokenError(token, serval_stream.reason)
            if serval_stream.status_code != 200:
                raise RhizomeHTTPStatusError(serval_stream)

            serval_reply_bytes = []
            lines = 0

            for c in serval_stream.iter_content():
                if c == b"\n":
                    lines += 1

                serval_reply_bytes.append(c)

                if (
                    c == b"]"
                    and lines == MESSAGELIST_HEADER_NEWLINES
                    and len(serval_reply_bytes) > MESSAGELIST_HEADER_SIZE
                ):
                    # complete json manually
                    serval_reply_bytes += [b"\n", b"]", b"\n", b"}"]
                    break

            serval_reply = b"".join(serval_reply_bytes)
            reply_json = json.loads(serval_reply)

            messages = unmarshall(json_table=reply_json, object_class=Message)
            return messages

    def send_message(self, sender, recipient, message):
        """Sends a message

        Args:
            sender (Union[ServalIdentity, str]): Either a ServalIdentity, or the SID of one
            recipient (Union[ServalIdentity, str]): Either a ServalIdentity, or the SID of one
            message (basestring)
        """
        if isinstance(sender, ServalIdentity):
            sender = sender.sid
        if isinstance(recipient, ServalIdentity):
            recipient = recipient.sid

        assert isinstance(
            sender, basestring
        ), "sender needs to be either a string or a ServalIdentity"
        assert isinstance(
            recipient, basestring
        ), "recipient needs to be either a string or a ServalIdentity"
        assert isinstance(message, basestring)

        self._low_level.send_message(
            sender=sender, recipient=recipient, message=message
        )

    def new_conversation(self, identity, other_identity, message):
        """Establishes a new conversation between two identities

        Args:
            identity (ServalIdentity)
            other_identity (ServalIdentity)
            message (basestring)

        Returns:
            Conversation
        """
        assert isinstance(identity, ServalIdentity)
        assert isinstance(other_identity, ServalIdentity)
        assert isinstance(message, basestring)

        self.send_message(sender=identity, recipient=other_identity, message=message)
        return self.get_conversation(identity=identity, other_identity=other_identity)
