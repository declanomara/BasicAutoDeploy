import json

from typing import Optional


def load_config(file: str = 'autodeploy.json') -> Optional[dict]:
    """
    This function takes a file path to a config and returns a dictionary containing the config.
    
    :param file: Path to config file to load
    :return: Returns a dictionary containing autodeploy config
    :rtype: dict
    """
    try:
        with open(file, 'r') as f:
            return json.loads(f.read())

    except FileNotFoundError:
        return None
