"""
pyserval.lowlevel.util
~~~~~~~~~~~~~

This module contains utility-methods
"""

from random import SystemRandom


def decode_json_table(json):
    """Transforms a 'JSON-table' (of the format below) into a List[dict], with each dict containing
    the data for a single object.

    Args:
        json (dict): A dictionary containing the json-table. Must be of the form:
                     {
                        'header': List[str],
                        'rows': List[List[str]]
                     }

    Note:
        See (https://github.com/servalproject/pyserval-dna/blob/development/doc/REST-API.md#json-table)
        for detailed description

    Returns:
        List[dict]: List of dictionaries containing separate JSON-objects
    """
    data = []

    for row in json["rows"]:
        # transform row of table
        # into dictionary for single object
        data.append(dict(zip(json["header"], row)))

    return data


def generate_secret():
    """Generate a (secure) 64 digit hey secret

    Can be used for bundle-secret

    Returns:
        str: String of 64 random hex-digits (32 bytes of random data)
    """
    randomiser = SystemRandom()
    secret = "".join([randomiser.choice("0123456789ABCDEF") for _ in range(64)])
    return secret


def unmarshall(json_table, object_class, **kwargs):
    """Unmarshalls a Json-Table into a list of Python-objects

    Args:
        json_table (dict): Dictionary containing the table data
        object_class: Class to unmarshall into
        kwargs: additional parameters for the object_class constructor

    Note:
        json_table has to be of the form:
        {
            'header': List[str],
            'rows': List[List[str]]
        }

    Returns:
        object_class: Instance of the specified class
                      initialised with the data from json_table and kwargs
    """
    json_data = decode_json_table(json_table)
    objects = []
    for data in json_data:
        data.update(**kwargs)
        objects.append(object_class(**data))
    return objects
