'''utility functions for commands'''

def listify(item):
    '''return the item as a list'''
    if isinstance(item, list):
        return item
    elif isinstance(item, dict):
        return item.items()
    else:
        return [item]

def flatten(x):
    '''flatten a list'''
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
