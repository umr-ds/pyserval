"""Tests for pyserval.meshmb"""

from hypothesis import given

from tests.custom_strategies import unicode_printable


@given(payload=unicode_printable)
def test_send_message(serval_init, payload):
    # FIXME: For some reason, if I try to tell hypothesis to only generate non-empty payloads it explodes
    if payload:
        identity = serval_init.keyring.default_identity()
        meshmb = serval_init.meshmb

        messages = meshmb.get_messages(feedid=identity)

        meshmb.send_message(identity=identity, message=payload)

        messages_new = meshmb.get_messages(feedid=identity)

        assert len(messages_new) == len(messages) + 1

        present = False
        for message in messages_new:
            if message.text == payload:
                present = True
                break

        assert present
