# grassformation/utils.py

import six
import copy

def change_requires_update(logger, attributes, old_values, current_values):
    ''' Given a list of attributes, compare the old and new values to see if
    there's been a change. '''
    for attribute in attributes:
        if (attribute not in old_values) and (attribute in current_values):
            logger.debug("New value for %s: %s" % (attribute, current_values[attribute]))
            return True
        if (attribute in old_values) and (attribute not in current_values):
            logger.debug("Value removed for %s: %s" % (attribute, old_values[attribute]))
            return True
        if (attribute in old_values) and (attribute in current_values):
            logger.debug("Evaluating %s: %s vs. %s" % (attribute, current_values[attribute], old_values[attribute]))
            if current_values[attribute] != old_values[attribute]:
                return True
    return False

def filter_dictionary(dictionary, keys):
    ''' Filters a dictionary for a set of given keys. '''
    return { key: dictionary[key] for key in keys if key in dictionary }

def val_to_bool(value):
    ''' Converts a value to a bool. '''
    if isinstance(value, six.string_types):
        return value.lower() in ['y', 'yes', 'true', 'on']
    else:
        return bool(value)

def keypath_search(obj, keypath, container=False, raise_keyerror=False):
    ''' Returns the element from a json-like object by keypath.

    Examples:
    ```
    >>> obj = {
        "a": {
            "b": {
                "3": 2,
                "43": 30,
                "c": [],
                "d": ['red', 'buggy', 'bumpers'],
            }
        }
    }
    >>> keypath_search(obj, 'a.b.d.1')
    'buggy'
    >>> keypath_search(obj, 'a.b.d.1', True)
    ['red', 'buggy', 'bumpers']
    >>> keypath_search(obj, 'a.b.d.1', True)[1] = 'foobar'
    >>> obj
    {'a': {'b': {'3': 2, '43': 30, 'c': [], 'd': ['red', 'foobar', 'bumpers']}}}
    ```

    Params:
        obj: The json-like object (nested dicts and/or lists)
        keypath: string. A period separated list of keys.
        container: bool. If set to True, the container of the one but last level
            is returned so this function can be used to update the input.
        raise_keyerror: bool. If set to True and no object found at the given
            keypath, a KeyError will be raised. Otherwise None is returned.

    Returns:
        The object found at the given keypath.
    '''
    keys = keypath.split('.')
    prev = None
    current = obj
    for key in keys:
        prev = current
        if isinstance(current, list):
            current = current[int(key)]
        elif isinstance(current, dict):
            if key in current:
                current = current[key]
            else:
                if raise_keyerror:
                    raise KeyError('No object found at {}'.format(keypath))
                else:
                    return prev if container else None
        else:
            raise ValueError('Unknown object type')
    return prev if container else current

def keypath_replace(obj, keypath, repl, inline=True):
    ''' Replaces an element at a given keypath in a json-like object.

    Params:
        obj: The json-like object (nested dicts and/or lists)
        keypath: string. A period separated list of keys.
        repl: callable. The current element will be passed as an argument.
        inline: bool. If set to False the replace will be carried out on a
            copy of the obj.

    Returns:
        True if the replacement was made.
    '''
    if not inline:
        obj = copy.deepcopy(obj)
    container = keypath_search(obj, keypath, container=True)
    last_key = keypath.split('.')[-1]
    if isinstance(container, list):
        last_key = int(last_key)
        container[last_key] = repl(container[last_key])
    else:
        if last_key in container:
            container[last_key] = repl(container[last_key])
    return obj
