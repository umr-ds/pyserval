# Python client for the serval-dna REST-interface

Provides a client to interact with serval-dna's REST-interface in python

## Functionality

The following REST-functionality is supported:

- Keyring
- Rhizome
- MeshMS
- MeshMB
- Route

For documentation on the specific endpoints, please consult [The serval-dna documentation](https://github.com/servalproject/serval-dna/blob/development/doc/REST-API.md)

## Dependencies

Up to `v0.4`, the code is compatible with both Python 2.7 & 3.4+. As of `v0.5`, you will need Python 3.6+

The only external runtime-dependency is [requests](https://github.com/requests/requests). This should be automatically installed by pip based on the package metadata.

Development dependencies are the following:

Automatic format checking is done using [black](https://github.com/ambv/black) and [pre-commit](https://github.com/pre-commit/pre-commit).

In order to run the tests, you will need [hypothesis](https://github.com/HypothesisWorks/hypothesis-python), [pytest](https://github.com/pytest-dev/pytest), and [pytest-cov](https://github.com/pytest-dev/pytest-cov) for coverage-reports.

To install all dependencies (both runtime and development/testing) run `pip install -r requirements.txt`

## Installation

As of `v0.4`, releases are uploaded to [PyPi](https://pypi.org/project/pyserval/), so you can just install it by name

`pip install pyserval`

## Development

In order to have reasonably well formatted code, a format-checking pre-commit hook is supplied. The tool used for checking/reformatting is [black](https://github.com/ambv/black). Note that the hook itself does not do any reformatting, it merely informs you that a file is not properly formatted. You need to do the reformatting yourself using `black $FILEPATH`.

The tests require you to have the `servald` binary from [serval-dna](https://github.com/servalproject/serval-dna) installed and available in your `$PATH`. In order to have a consistent testing enviroment, `/tmp/pyserval-tests/` will be used as the `$SERVALINSTANCE_PATH`.

1. Clone Project
2. Install project to python-path
    - You might want to use a virtualenv
    - You might also want to do an editable install with `pip install -e .`
3. Install development dependencies with `pip install -r requirements.txt`
4. Install git pre-commit hook with `pre-commit install`
5. For testing: In the project root run `pytest --cov=pyserval`
