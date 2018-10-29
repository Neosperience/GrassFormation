# utils/keypath.py

import copy

''' Utility functions for accessing elements of json-like object by keypath.'''

def search(obj, keypath, container=False, raise_keyerror=False):
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
            raise ValueError('Can not get object at keypath "{}" from json-like object: Unknown object type.'.format(keypath))
    return prev if container else current

def replace(obj, keypath, repl, inline=True):
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
    container = search(obj, keypath, container=True)
    last_key = keypath.split('.')[-1]
    if isinstance(container, list):
        last_key = int(last_key)
        container[last_key] = repl(container[last_key])
    else:
        if last_key in container:
            container[last_key] = repl(container[last_key])
    return obj
