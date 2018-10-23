# -*- coding: utf-8 -*-
"""
pyserval.meshmb
~~~~~~~~~~~~~~~

This module contains the means to publish and subscribe MeshMB feeds
"""

from pyserval.lowlevel.util import decode_json_table, unmarshall


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
        connection (connection.RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection):
        self._connection = connection

    def send_message(
        self, identity, message, message_type="text/plain", charset="utf-8"
    ):
        """Sends a message to a feed

        Endpoint:
            POST /restful/meshmb/ID/sendmessage

        Args:
            identity (str): Signing ID of an unlocked Identity in the keyring
                            Is also the Feed ID
            message (str): content of the message
            message_type (str): MIME-type of the message (default: text/plain)
            charset (str): Character encoding (default: utf-8)
        """
        multipart = [
            (
                "message",
                ("message1", message, "{};charset={}".format(message_type, charset)),
            )
        ]
        self._connection.post(
            "/restful/meshmb/{}/sendmessage".format(identity), files=multipart
        )

    def get_messages(self, feedid):
        """Get all the messages of a feed

        Endpoint:
            GET /restful/meshmb/FEEDID/messagelist.json

        Args:
            feedid (str): Feed ID (is also Signing ID of the feed author)

        Returns:
            List[BroadcastMessage]: All the messages sent to this feed
        """
        result = self._connection.get(
            "/restful/meshmb/{}/messagelist.json".format(feedid)
        ).json()
        messages = unmarshall(json_table=result, object_class=BroadcastMessage)
        return messages

    def follow_feed(self, identity, feedid):
        """Follows a feed

        Endpoint:
            POST /restful/meshmb/ID/follow/FEEDID

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should follow the feed
            feedid (str): Feed ID
        """
        self._connection.post("/restful/meshmb/{}/follow/{}".format(identity, feedid))

    def unfollow_feed(self, identity, feedid):
        """Unfollows a feed

        Endpoint:
            POST /restful/meshmb/ID/ignore/FEEDID

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should unfollow the feed
            feedid (str): Feed ID
        """
        self._connection.post("/restful/meshmb/{}/ignore/{}".format(identity, feedid))

    def get_feedlist(self, identity):
        """Get a list of all followed identities

        Endpoint:
            GET /restful/meshmb/ID/feedlist.json

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring

        Returns:
            List[Feed]: List of all feeds that the specified identity is currently following
        """
        result = self._connection.get(
            "/restful/meshmb/{}/feedlist.json".format(identity)
        ).json()
        feeds = unmarshall(json_table=result, object_class=Feed, meshmb=self)
        return feeds

    def get_activity(self, identity):
        """Get all the messages from followed feeds

        Endpoint:
            GET /restful/meshmb/ID/activity.json

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring

        Returns:
            List[BroadcastMessage]: List of all messages from all feeds that
                                    the specified identity is currently following
                                    (in chronological order)
        """
        result = self._connection.get(
            "/restful/meshmb/{}/activity.json".format(identity)
        ).json()
        message_data = decode_json_table(result)
        for data in message_data:
            data["token"] = data.pop(".token")
            data["text"] = data.pop("message")
        messages = [BroadcastMessage(**data) for data in message_data]
        return messages
