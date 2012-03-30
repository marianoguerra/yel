'''utility functions for commands'''

TYPE_CHECKS = {
    "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
    "decimal": lambda x: isinstance(x, float),
    "number": lambda x: (isinstance(x, float) or
        isinstance(x, int) and not
        isinstance(x, bool)),
    "string": lambda x: isinstance(x, basestring),
    "boolean": lambda x: isinstance(x, bool),
    "none": lambda x: x is None,
    "list": lambda x: isinstance(x, list),
    "object": lambda x: isinstance(x, dict),
    # javascript falsy values
    "falsy": lambda x: x == False or x == 0 or x == 0.0 or x == None,
    "truthy": lambda x: not (x == False or x == 0 or x == 0.0 or x == None)
}

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

def expect_list(item, name="value"):
    '''raise ValueError if item is not a list instance'''
    return expect_type(item, name, list)

def expect_int(item, name="value"):
    '''raise ValueError if item is not a int instance'''
    return expect_type(item, name, int)

def expect_type(item, name, type_, msg="expected %s for %s, got: %s"):
    '''raise ValueError if item is not an instance of type_'''
    if not isinstance(item, type_):
        raise ValueError(msg % (type_.__name__, name, str(item)))

    return item

def expect_list_of(type_, items, name="items"):
    '''raise ValueError if items is not a list of type_'''
    if not isinstance(items, list):
        raise ValueError("expected list of %s for %s, got: %s" % (
            type_.__name__, name, str(items)))
    else:
        for item in items:
            expect_type(item, name, type_,
                    "expected list of %s for %s, got item: %s")

    return items

def expect_arg_type(args, key, type_, default=None, name=None):
    '''try to get args[key], check if it's type *type_* if not raise ValueError
    if not found return default'''

    if name is None:
        name = key

    if key in args:
        result = args[key]
        expect_type(result, name, type_)
    else:
        result = default

    return result
