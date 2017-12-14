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

In order to run the tests, you will need [hypothesis](https://github.com/HypothesisWorks/hypothesis-python) and [pytest](https://github.com/pytest-dev/pytest), as well as [pytest-cov](https://github.com/pytest-dev/pytest-cov) for coverage-reports.

## Installation

`pip install https://github.com/umr-ds/pyserval/archive/v0.1.2.tar.gz`

## Running the tests

The tests require you to have `servald` from [serval-dna](https://github.com/servalproject/serval-dna) installed and available in your `PATH`. In order to have a consistent testing enviroment, a directory `/tmp/pyserval-tests/` to be used as the `SERVALINSTANCE_PATH`.

1. Clone Project
2. Install project to python-path
    - You might want to use a virtualenv
    - You might also want to do an editable install with `pip install -e .`
3. Install testing dependencies with `pip install .[test]`
4. In the project root run `pytest --cov=pyserval`