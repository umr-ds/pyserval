# -*- coding: utf-8 -*-
"""
pyserval.meshmb
~~~~~~~~~~~~~~~

This module contains the means to publish and subscribe MeshMB feeds
"""

from pyserval.lowlevel.meshmb import LowLevelMeshMB


class BroadcastMessage:
    """One-to-many broadcast message

    Args:
        id (str): ID of this message
        author (str): SID of the authors identity
        name (str): (?)
        offset (int): Offset of this message in the conversation's ply
        ack_offset (int): (?)
        token (str): token for real-time access (not implemented)
        text (str): Content of the message
        timestamp (int): UNIX-timestamp of when the message was sent

    Attributes:
        id (str): ID of this message
        author (str): SID of the authors identity
        name (str): (?)
        offset (int): Offset of this message in the conversation's ply
        ack_offset (int): (?)
        token (str): token for real-time access (not implemented)
        text (str): Text of the message
        timestamp (int): UNIX-timestamp of when the message was sent
    """

    def __init__(
        self,
        id=None,
        author=None,
        name=None,
        offset=None,
        ack_offset=None,
        token=None,
        text=None,
        timestamp=None,
    ):
        self.offset = offset
        self.token = token
        self.text = text
        self.timestamp = timestamp
        self.id = id
        self.author = author
        self.name = name
        self.ack_offset = ack_offset

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class Feed:
    """Feed of broadcast messages

    Args:
        meshmb (MeshMB): Interface-object to interact with the MeshMB REST-interface
        id (str): Feed ID (senders Signing ID)
        author (str): Senders SID
        blocked (bool): (?)
        name (str): (?)
        timestamp (int): UNIX-timestamp of the latest message (?)
        last_message (str): Content of the last message

    Attributes:
        id (str): Feed ID (senders Signing ID)
        author (str): Senders SID
        blocked (bool): (?)
        name (str): (?)
        timestamp (int): UNIX-timestamp of the latest message (?)
        last_message (str): Content of the last message

    """

    def __init__(self, meshmb, id, author, blocked, name, timestamp, last_message):
        self._meshmb = meshmb
        self.id = id
        self.author = author
        self.blocked = blocked
        self.name = name
        self.timestamp = timestamp
        self.last_message = last_message

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def follow(self, identity):
        """Follow this feed

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should follow this feed
        """
        self._meshmb.follow_feed(identity=identity, feedid=self.id)

    def unfollow(self, identity):
        """Unfollow this feed

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should unfollow this feed
        """
        self._meshmb.unfollow_feed(identity=identity, feedid=self.id)

    def get_messages(self):
        """Gets all the messages from this feed"""
        self._meshmb.get_messages(self.id)


class MeshMB:
    """Interface to interact with the MeshMB REST-interface

    Args:
        low_level_meshmb (LowLevelMeshMB): Used to perform low level requests
    """

    def __init__(self, low_level_meshmb):
        self._low_level_meshmb = low_level_meshmb
