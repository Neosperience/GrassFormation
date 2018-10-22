# grassformation/utils.py

import six

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
