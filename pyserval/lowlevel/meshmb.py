# -*- coding: utf-8 -*-
"""
pyserval.lowlevel.meshmb
~~~~~~~~~~~~~~~

This module contains the means to publish and subscribe MeshMB feeds
"""

from pyserval.lowlevel.util import decode_json_table, unmarshall


class LowLevelMeshMB:
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
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get(
            "/restful/meshmb/{}/messagelist.json".format(feedid)
        )

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
            requests.models.Response: Response returned by the serval-server
        """
        return self._connection.get("/restful/meshmb/{}/feedlist.json".format(identity))

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
