# Python client for the serval-dna REST-interface

Provides a client to interact with serval-dna's REST-interface natively in python

## Functionality

The following functionality is implemented:

- Serval Keyring
- Rhizome (except GET /restful/rhizome/newsince[/TOKEN]/bundlelist.json)
- MeshMS (except GET /restful/meshms/SENDERSID/RECIPIENTSID/newsince[/TOKEN]/messagelist.json)
- MeshMB

For documentation on the specific enpoints, please consult [The serval-dna socumentation](https://github.com/servalproject/serval-dna/blob/development/doc/REST-API.md)

## Dependencies

This code should run ob both Python 2.7 and 3.4+

The only external dependency is [requests](https://github.com/requests/requests)

In order to run the tests, you will need [hypothesis](https://github.com/HypothesisWorks/hypothesis-python) and [pytest](https://github.com/pytest-dev/pytest)

## Installation

`pip install https://github.com/umr-ds/pyserval/archive/v0.1.1.tar.gz`

## Running tests

Clone project, go to root directory and run `pytest`