"""
pyserval.route
~~~~~~~~~~~~~~~~

This module contains the means to interact with servald's routing-interface
"""

from pyserval.lowlevel.route import LowLevelRoute
from pyserval.lowlevel.util import unmarshall
from typing import Union, List


class Peer:
    """Representation of a serval peer

    Args:
        _route (Route): Interface-object to interact with the routing REST-interface
        sid (str): the SID of the identity, as 64 uppercase hex digits
        did (Union[str, None]): the DID of the identity if known (eg, for a local keyring identity)
        name (Union[str, None]): the Name of the identity if known (eg, for a local keyring identity)
        is_self (bool): true if the identity is a self-identity, ie, in the local keyring
        reachable_broadcast (bool): true if the identity is reachable by broadcast link
        reachable_unicast (bool): true if the identity is reachable by unicast link
        reachable_indirect (bool) true if the identity is reachable only via another node
        interface (Union[str, None]): the name of the local network interface on which the identity is reachable
        hop_count (int): the number of hops to reach the identity
        first_hop (Union[str, None]): if hop_count > 1, then the SID of the first identity in the route
        penultimate_hop (Union[str, None]): if hop_count > 2, then the SID of the penultimate identity in the route
    """

    def __init__(
        self,
        _route,
        sid: str,
        did: Union[str, None],
        name: Union[str, None],
        is_self: bool,
        reachable_broadcast: bool,
        reachable_unicast: bool,
        reachable_indirect: bool,
        interface: Union[str, None],
        hop_count: int,
        first_hop: Union[str, None],
        penultimate_hop: Union[str, None],
    ):
        self._route = _route
        self.sid = sid
        self.did = did
        self.name = name
        self.is_self = is_self
        self.reachable_broadcast = reachable_broadcast
        self.reachable_unicast = reachable_unicast
        self.reachable_indirect = reachable_indirect
        self.interface = interface
        self.hop_count = hop_count
        self.first_hop = first_hop
        self.penultimate_hop = penultimate_hop


class Route:
    """Interface for interacting with the serval route API

    Args:
        low_level_route (LowLevelRoute): Used to perform low level requests
    """

    def __init__(self, low_level_route: LowLevelRoute):
        assert isinstance(low_level_route, LowLevelRoute)
        self._route = low_level_route

    def get_all(self) -> List[Peer]:
        """Get all known peers

        Returns:
            List[Peer]: List of peer-object containing metadata of all known peers
        """
        serval_response = self._route.get_all()
        response_json = serval_response.json()

        peers = unmarshall(json_table=response_json, object_class=Peer, _route=self)

        return peers
