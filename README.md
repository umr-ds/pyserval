# Python client for the serval-dna REST-interface

Provides a client to interact with serval-dna's REST-interface natively in python

## Functionality

The following functionality is implemented:

- Serval Keyring
- Rhizome
- MeshMS
- MeshMB
- Route

For documentation on the specific enpoints, please consult [The serval-dna socumentation](https://github.com/servalproject/serval-dna/blob/development/doc/REST-API.md)

## Dependencies

This code should run on both Python 2.7 and 3.4+

The only external (runtime-)dependency is [requests](https://github.com/requests/requests)

Development dependencies are the following:

Automatic format checking is done using [black](https://github.com/ambv/black) and [pre-commit](https://github.com/pre-commit/pre-commit).

In order to run the tests, you will need [hypothesis](https://github.com/HypothesisWorks/hypothesis-python) and [pytest](https://github.com/pytest-dev/pytest), as well as [pytest-cov](https://github.com/pytest-dev/pytest-cov) for coverage-reports.

## Installation

`pip install https://github.com/umr-ds/pyserval/releases/download/v0.3.4/pyserval-0.3.4-py2.py3-none-any.whl`

## Development

In order to have reasonably well formatted code, a format-checking pre-commit hook is supplied. The tool used for checking/reformatting is [black](https://github.com/ambv/black). Note that the hook itself does not do any reformatting, it merely informs you that a file is not properly formatted. You need to do the reformatting yourself using `black $FILEPATH`.

The tests require you to have `servald` from [serval-dna](https://github.com/servalproject/serval-dna) installed and available in your `PATH`. In order to have a consistent testing enviroment, `/tmp/pyserval-tests/` will be used as the `SERVALINSTANCE_PATH`.

1. Clone Project
2. Install project to python-path
    - You might want to use a virtualenv
    - You might also want to do an editable install with `pip install -e .`
3. Install development dependencies with `pip install -r requirements.txt`
4. Install git pre-commit hook with `pre-commit install`
5. For testing: In the project root run `pytest --cov=pyserval`
