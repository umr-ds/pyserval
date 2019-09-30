"""Tests for pyserval.meshms"""

from hypothesis import given

from tests.custom_strategies import unicode_printable


@given(payload=unicode_printable)
def test_send_message(serval_init, payload):
    # FIXME: For some reason, if I try to tell hypothesis to only generate non-empty payloads it explodes
    if payload:
        meshms = serval_init.meshms
        identities = serval_init.keyring.get_or_create(2)

        messages = meshms.message_list(sender=identities[0], recipient=identities[1])

        meshms.send_message(
            sender=identities[0], recipient=identities[1], message=payload
        )

        messages_new = meshms.message_list(
            sender=identities[0], recipient=identities[1]
        )

        assert len(messages_new) == len(messages) + 1

        present = False
        for message in messages_new:
            if message.text == payload:
                present = True
                break

        assert present
