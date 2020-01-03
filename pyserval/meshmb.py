"""
pyserval.meshmb
~~~~~~~~~~~~~~~

This module contains the means to publish and subscribe MeshMB feeds
"""

from pyserval.lowlevel.meshmb import LowLevelMeshMB
from pyserval.keyring import ServalIdentity
from pyserval.lowlevel.util import unmarshall, decode_json_table
from pyserval.exceptions import RhizomeHTTPStatusError
from typing import Union, List


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
        id: Union[str, None] = None,
        author: Union[str, None] = None,
        name: Union[str, None] = None,
        offset: Union[int, None] = None,
        ack_offset: Union[int, None] = None,
        token: Union[str, None] = None,
        text: Union[str, None] = None,
        timestamp: Union[int, None] = None,
    ) -> None:
        self.offset = offset
        self.token = token
        self.text = text
        self.timestamp = timestamp
        self.id = id
        self.author = author
        self.name = name
        self.ack_offset = ack_offset

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
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

    def __init__(
        self,
        meshmb,
        id: str,
        author: str,
        blocked: bool,
        name: str,
        timestamp: int,
        last_message: str,
    ):
        self._meshmb = meshmb
        self.id = id
        self.author = author
        self.blocked = blocked
        self.name = name
        self.timestamp = timestamp
        self.last_message = last_message

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def follow(self, identity: str) -> None:
        """Follow this feed

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should follow this feed
        """
        self._meshmb.follow_feed(identity=identity, feedid=self.id)

    def unfollow(self, identity: str) -> None:
        """Unfollow this feed

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should unfollow this feed
        """
        self._meshmb.unfollow_feed(identity=identity, feedid=self.id)

    def get_messages(self) -> None:
        """Gets all the messages from this feed"""
        self._meshmb.get_messages(self.id)


class MeshMB:
    """Interface to interact with the MeshMB REST-interface

    Args:
        low_level_meshmb (LowLevelMeshMB): Used to perform low level requests
    """

    def __init__(self, low_level_meshmb: LowLevelMeshMB):
        self._low_level_meshmb = low_level_meshmb

    def send_message(
        self, identity: Union[ServalIdentity, str], message: Union[bytes, str]
    ) -> None:
        """Sends a message to a feed

        Args:
            identity (Union[ServalIdentity, str]): Keyring identity or corresponding SID
            message (Union[bytes, str]): Message payload
        """
        if isinstance(identity, ServalIdentity):
            identity = identity.identity

        assert isinstance(
            identity, str
        ), "identity must be either a ServalIdentity or SID-string"

        if isinstance(message, str):
            message_type = "text/plain"
            charset = "utf-8"
        else:
            message_type = "application/octet-stream"
            charset = None

        assert message, "message must be non-empty"

        result = self._low_level_meshmb.send_message(
            identity=identity,
            message=message,
            message_type=message_type,
            charset=charset,
        )

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200 and result.status_code != 201:
            raise RhizomeHTTPStatusError(result)

    def get_messages(
        self, feedid: Union[ServalIdentity, str]
    ) -> List[BroadcastMessage]:
        """Get all the messages of a feed

        Args:
            feedid (Union[ServalIdentity, str]): Keyring identity or corresponding Signing-ID
                                                 NOTE: This is NOT the same as the SID

        Returns:
            List[BroadcastMessage]: All the messages sent to this feed
        """
        if isinstance(feedid, ServalIdentity):
            feedid = feedid.identity

        assert isinstance(
            feedid, str
        ), "feedid must be either a ServalIdentity or Identity-string"

        result = self._low_level_meshmb.get_messages(feedid=feedid)

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)

        result_json = result.json()
        messages = unmarshall(json_table=result_json, object_class=BroadcastMessage)
        return messages

    def get_feedlist(self, identity: Union[ServalIdentity, str]) -> List[Feed]:
        """Get a list of all followed identities

        Args:
            identity (Union[ServalIdentity, str]): Keyring identity or corresponding Signing-ID
                                                   NOTE: This is NOT the same as the SID

        Returns:
            List[Feed]: List of all feeds that the specified identity is currently following
        """
        if isinstance(identity, ServalIdentity):
            identity = identity.identity

        assert isinstance(
            identity, str
        ), "identity must be either a ServalIdentity or Identity-string"

        result = self._low_level_meshmb.get_feedlist(identity=identity)

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)

        result_json = result.json()
        feeds = unmarshall(json_table=result_json, object_class=Feed, meshmb=self)
        return feeds

    def get_activity(
        self, identity: Union[ServalIdentity, str]
    ) -> List[BroadcastMessage]:
        """Get all the messages from followed feeds

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring

        Returns:
            List[BroadcastMessage]: List of all messages from all feeds that
                                    the specified identity is currently following
                                    (in chronological order)
        """
        if isinstance(identity, ServalIdentity):
            identity = identity.identity

        assert isinstance(
            identity, str
        ), "identity must be either a ServalIdentity or Identity-string"

        result = self._low_level_meshmb.get_activity(identity=identity)

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)

        result_json = result.json()
        message_data = decode_json_table(result_json)
        for data in message_data:
            data["token"] = data.pop(".token")
            data["text"] = data.pop("message")
        messages = [BroadcastMessage(**data) for data in message_data]
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
        if isinstance(identity, ServalIdentity):
            identity = identity.identity

        assert isinstance(
            identity, str
        ), "identity must be either a ServalIdentity or Identity-string"

        result = self._low_level_meshmb.follow_feed(identity=identity, feedid=feedid)

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)

    def unfollow_feed(self, identity: str, feedid: str) -> None:
        """Unfollows a feed

        Endpoint:
            POST /restful/meshmb/ID/ignore/FEEDID

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should unfollow the feed
            feedid (str): Feed ID
        """
        if isinstance(identity, ServalIdentity):
            identity = identity.identity

        assert isinstance(
            identity, str
        ), "identity must be either a ServalIdentity or Identity-string"

        result = self._low_level_meshmb.unfollow_feed(identity=identity, feedid=feedid)

        # I would like to make a better distinction here, but unfortunately the upstream docs
        # do not specify any status codes for specific errors
        if result.status_code != 200:
            raise RhizomeHTTPStatusError(result)
