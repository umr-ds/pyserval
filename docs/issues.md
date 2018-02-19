# Serval-REST issues

## Keychain
* DID truncates to 31 bytes
* Name truncates to 63 bytes (may break utf-8)
* the `GET /restful/keyring/SID/lock` endpoint appears to not to be implemented, even though it is part of the documentation
