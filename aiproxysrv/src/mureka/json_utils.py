"""
JSON utilities for Mureka API responses
"""


def prune_keys(data, keys):
    """
    Remove all occurrences of specified keys from nested dict/list structures.

    Args:
        data: Dictionary or list to process
        keys: Set of keys to remove

    Returns:
        Cleaned data structure with specified keys removed
    """
    if isinstance(data, dict):
        return {k: prune_keys(v, keys) for k, v in data.items() if k not in keys}
    if isinstance(data, list):
        return [prune_keys(item, keys) for item in data]
    return data
