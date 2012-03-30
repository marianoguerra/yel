#!/usr/bin/env python
'''command repository'''
import os
import sys
import json
import random

import util

from command import Command, Result

COMMANDS = {}

class Environment(Command):
    '''command to manipulate the environment'''

    SHORT = "env"
    LONG = "environemnt"

    USAGE = '''env get foo; env get foo "default"; env set foo "value"'''

    EXPAND_SHORT_OPTIONS = {
        "f": "fail"
    }

    def __init__(self, args, vars_):
        Command.__init__(self, self.SHORT, args, vars_)

    def run(self):
        '''run the command and return result'''

        args = self.get_default_args()
        value = None

        if len(args) == 2:
            action, name = args
        elif len(args) == 3:
            action, name, value = args
        else:
            return Result.bad_request("expected 2 or 3 args")

        if action == "get":
            fail = self.args.get("fail", False)
            result = self.get(name, value, fail)
        elif action == "set":
            result = self.set(name, value)
        else:
            return Result.bad_request("expected valid action get or set")

        return Result.ok(result)

class MultiTypeCommand(Command):
    '''base command that modifies arguments dependent on type'''

    def __init__(self, args, vars_):
        Command.__init__(self, self.SHORT, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return items

    def process_object(self, items):
        '''do the process on object'''
        return items

    def process_single(self, item):
        '''do the process on single value'''
        return item

    def run(self):
        '''run the command and return result'''
        args = self.get_args()

        if isinstance(args, list):
            return Result.ok(self.process_list(args))
        elif isinstance(args, dict):
            # if it's a dict and there are default arguments remove them
            if Command.DEFS in args:
                del args[Command.DEFS]

            return Result.ok(self.process_object(args))
        else:
            return Result.ok(self.process_single(args))

class Echo(MultiTypeCommand):
    '''command to reply the received arguments'''
    SHORT = "echo"
    LONG = "echo"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

class Size(MultiTypeCommand):
    '''return the size of the arguments'''

    SHORT = "size"
    LONG = "size"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return len(items)

    def process_object(self, items):
        '''do the process on object'''
        return len(items)

    def process_single(self, item):
        '''do the process on single value'''
        return 1

class Range(MultiTypeCommand):
    '''return a range of numbers from the arguments'''

    SHORT = "range"
    LONG = "range"

    EXPAND_SHORT_OPTIONS = {
        "f": "from",
        "t": "to",
        "s": "step"
    }

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        frm  = 0
        to   = 1
        step = 1

        if not all(isinstance(item, int) for item in items):
            raise ValueError("expected 1, 2 or 3 integers, got: " + str(items))

        if len(items) == 1:
            to = items[0]
        elif len(items) == 2:
            frm, to = items
        elif len(items) == 3:
            frm, to, step = items

            if step < 0:
                frm, to = to, frm

        else:
            raise ValueError("expected 1, 2 or 3 integers, got: " + str(items))

        return list(range(frm, to, step))

    def process_object(self, items):
        '''do the process on object'''
        return len(items)

    def process_single(self, item):
        '''do the process on single value'''
        return self.process_list([item])

class Keys(MultiTypeCommand):
    '''return the keys of the arguments'''

    SHORT = "keys"
    LONG = "keys"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return []

    def process_object(self, items):
        '''do the process on object'''
        return items.keys()

    def process_single(self, item):
        '''do the process on single value'''
        return []

class Values(MultiTypeCommand):
    '''return the values of the arguments'''

    SHORT = "values"
    LONG = "values"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return items

    def process_object(self, items):
        '''do the process on object'''
        return items.values()

    def process_single(self, item):
        '''do the process on single value'''
        return [item]

class Items(MultiTypeCommand):
    '''return the a list of key value pairs of the arguments'''

    SHORT = "items"
    LONG = "items"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return list(enumerate(items))

    def process_object(self, items):
        '''do the process on object'''
        return items.items()

    def process_single(self, item):
        '''do the process on single value'''
        return [[0, item]]

class List(MultiTypeCommand):
    '''return a list representation of the arguments'''

    SHORT = "list"
    LONG = "list"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return items

    def process_object(self, items):
        '''do the process on object'''
        return items.items()

    def process_single(self, item):
        '''do the process on single value'''
        return [item]

class Flatten(MultiTypeCommand):
    '''return a flat list representation of the arguments'''

    SHORT = "flatten"
    LONG = "flatten"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return util.flatten(items)

    def process_object(self, items):
        '''do the process on object'''
        return util.flatten(items.items())

    def process_single(self, item):
        '''do the process on single value'''
        return [item]

class Reverse(MultiTypeCommand):
    '''command to reverse the received arguments if they are a list
    leave them untouched otherwise'''
    SHORT = "reverse"
    LONG = "reverse"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        items.reverse()
        return items

class Shuffle(MultiTypeCommand):
    '''command to shuffle the content of the arguments if is a list'''
    SHORT = "shuffle"
    LONG = "shuffle"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        random.shuffle(items)
        return items

class Min(MultiTypeCommand):
    '''command to get the minimum value from arguments if is a list'''
    SHORT = "min"
    LONG = "minimum"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        # TODO: define how to handle list with different types
        return min(items)

class Max(MultiTypeCommand):
    '''command to get the maximum value from arguments if is a list'''
    SHORT = "max"
    LONG = "maximum"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        # TODO: define how to handle list with different types
        return max(items)

class Set(MultiTypeCommand):
    '''command to get a list with duplicated values removed from arguments if
    is a list'''

    SHORT = "set"
    LONG = "set"

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        return list(set(items))

class Slice(MultiTypeCommand):
    '''command to get a sublist from arguments if is a list'''

    SHORT = "slice"
    LONG = "slice"

    EXPAND_SHORT_OPTIONS = {
        "f": "from",
        "t": "to",
        "s": "step"
    }

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_object(self, items):
        '''do the process on items'''

        defs = self.get_default_args()

        util.expect_list(defs)

        arg_from = self.get_arg_type("from", int, None)
        arg_to   = self.get_arg_type("to", int, None)
        arg_step = self.get_arg_type("step", int, None)

        if arg_step is not None and arg_step < 0:
            arg_from, arg_to = arg_to, arg_from

        return defs[arg_from:arg_to:arg_step]

class Item(MultiTypeCommand):
    '''command to get a sublist from arguments if is a list'''

    SHORT = "item"
    LONG = "item"

    EXPAND_SHORT_OPTIONS = {
        "i": "item"
    }

    def __init__(self, args, vars_):
        MultiTypeCommand.__init__(self, args, vars_)

    def process_list(self, items):
        '''do the process on items'''
        if len(items) > 0:
            return items[0]
        else:
            return items

    def process_object(self, items):
        '''do the process on items'''

        defs = self.get_default_args()
        util.expect_list(defs)
        index = self.args.get("item", 0)

        if len(defs) > 0:
            return defs[index]
        else:
            return defs

class Filter(Command):
    '''command to filter items in a list if satisfy a predicate'''
    SHORT = "filter"
    LONG = "filter"

    FILTERS = {
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
        "falsy": lambda x: x == False or x == 0 or x == 0.0 or x == None
    }

    EXPAND_SHORT_OPTIONS = {
        "t": "type"
    }

    def __init__(self, args, vars_):
        Command.__init__(self, self.SHORT, args, vars_)
        self.modifier = lambda f: lambda x: not f(x)
        self.multichecker = all

    def run(self):
        '''run the command and return result'''
        items = self.args.get(Command.DEFS, None)

        if items is None:
            items = json.load(sys.stdin)

        filter_names = self.args.get("type", None)

        if filter_names is None:
            return Result.bad_request("filter not specified")
        else:
            checks = []

            for name in filter_names:
                if name not in self.FILTERS:
                    return Result.bad_request("filter not found: " + str(name))
                else:
                    filter_fun = self.FILTERS[name]
                    checks.append(self.modifier(filter_fun))

            result = []
            for item in items:
                if self.multichecker(check(item) for check in checks):
                    result.append(item)

            return Result.ok(result)

class Keep(Filter):
    '''keep items in a list if satisfy a predicate'''
    SHORT = "keep"
    LONG = "keep"

    def __init__(self, args, vars_):
        Filter.__init__(self, args, vars_)
        self.modifier = lambda f: lambda x: f(x)
        self.multichecker = any

def load_commands():
    '''load available commands'''
    for attr in globals().values():

        if (type(attr) == type and issubclass(attr, Command) and
                hasattr(attr, "SHORT")):
            COMMANDS[attr.SHORT] = attr
            COMMANDS[attr.LONG] = attr

def main(args):
    '''generic command entry point'''

    name = os.path.basename(args[0])

    if name.startswith("@"):
        name = name[1:]

    if name not in COMMANDS:
        finish(Result.not_found("command %s not found" % name))

    cls = COMMANDS[name]

    params = cls.parse_args(args[1:])

    result = cls.invoke(dict(name=name, args=params, vars=os.environ))
    finish(result)

def finish(result):
    '''finish the program'''
    if result.status != Result.OK and result.reason:
        sys.stderr.write(result.reason)
        sys.stderr.write('\n')
        sys.stderr.flush()

    sys.stdout.write(json.dumps(result.result))
    sys.stdout.write('\n')
    sys.stdout.flush()
    sys.exit(result.status)

if __name__ == "__main__":
    load_commands()
    main(sys.argv)
