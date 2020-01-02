"""
pyserval.lowlevel.meshmb
~~~~~~~~~~~~~~~

This module contains the means to publish and subscribe MeshMB feeds
"""

from pyserval.connection import RestfulConnection
from requests.models import Response


class LowLevelMeshMB:
    """Interface to interact with the MeshMB REST-interface

    Args:
        connection (connection.RestfulConnection): Used for HTTP-communication
    """

    def __init__(self, connection: RestfulConnection) -> None:
        assert isinstance(connection, RestfulConnection)
        self._connection = connection

    def send_message(
        self,
        identity: str,
        message: str,
        message_type: str = "text/plain",
        charset: str = "utf-8",
    ) -> Response:
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
            ("message", ("message1", message, f"{message_type};charset={charset}"),)
        ]
        return self._connection.post(
            f"/restful/meshmb/{identity}/sendmessage", files=multipart
        )

    def get_messages(self, feedid: str) -> Response:
        """Get all the messages of a feed

        Endpoint:
            GET /restful/meshmb/FEEDID/messagelist.json

        Args:
            feedid (str): Feed ID (is also Signing ID of the feed author)

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get(f"/restful/meshmb/{feedid}/messagelist.json")

    def follow_feed(self, identity: str, feedid: str) -> Response:
        """Follows a feed

        Endpoint:
            POST /restful/meshmb/ID/follow/FEEDID

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should follow the feed
            feedid (str): Feed ID
        """
        return self._connection.post(f"/restful/meshmb/{identity}/follow/{feedid}")

    def unfollow_feed(self, identity: str, feedid: str) -> Response:
        """Unfollows a feed

        Endpoint:
            POST /restful/meshmb/ID/ignore/FEEDID

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring
                            which should unfollow the feed
            feedid (str): Feed ID
        """
        return self._connection.post(f"/restful/meshmb/{identity}/ignore/{feedid}")

    def get_feedlist(self, identity: str) -> Response:
        """Get a list of all followed identities

        Endpoint:
            GET /restful/meshmb/ID/feedlist.json

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get(f"/restful/meshmb/{identity}/feedlist.json")

    def get_activity(self, identity: str) -> Response:
        """Get all the messages from followed feeds

        Endpoint:
            GET /restful/meshmb/ID/activity.json

        Args:
            identity (str): Signing ID of an (unlocked) identity in the keyring

        Returns:
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get(f"/restful/meshmb/{identity}/activity.json")
