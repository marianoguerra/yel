'''base yel command'''
import os
import sys
import json

import util

DEBUG = os.environ.get("YEL_DEBUG", False)
STRICT_MODE = os.environ.get("YEL_STRICT", False)

class JsonSerializable(object):
    '''class that can be serialized to/from json'''

    def to_json(self):
        '''return json representation'''
        return vars(self)

    def to_json_string(self):
        '''return json string representation'''
        return json.dumps(self.to_json())


class Result(JsonSerializable):
    '''command execution result'''

    OK = 200
    CREATED = 201

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404

    ERROR = 500

    REASONS = {
        OK: "ok",
        CREATED: "created",
        BAD_REQUEST: "bad request",
        UNAUTHORIZED: "unauthorized",
        NOT_FOUND: "not found",
        ERROR: "error"
    }

    def __init__(self, result, status=OK, reason=None):
        JsonSerializable.__init__(self)

        self.status = status

        if reason is None:
            self.reason = Result.status_to_reason(status)
        else:
            self.reason = reason

        self.result = result

    @classmethod
    def status_to_reason(cls, status):
        '''return a string representation of a status'''
        return cls.REASONS.get(status, "unknown")

    @classmethod
    def bad_request(cls, reason):
        '''return a bad request result'''
        return cls(None, cls.BAD_REQUEST, reason)

    @classmethod
    def ok(cls, result):
        '''return an ok result'''
        return cls(result, cls.OK)

    @classmethod
    def not_found(cls, reason):
        '''return a not found result'''
        return cls(None, cls.NOT_FOUND, reason)

    @classmethod
    def from_exception(cls, ex):
        '''return a result from an exception'''
        return cls(None, cls.ERROR, str(ex))

class Command(JsonSerializable):
    '''base command'''

    SHORT = "nop"
    LONG = "no-operation"

    EXPAND_SHORT_OPTIONS = {}

    DEFS = "__defaults__"

    def __init__(self, name, args, vars_):
        JsonSerializable.__init__(self)

        self.name = name
        self.args = args
        self.vars = vars_

        self.defs = self.args.get(Command.DEFS, None)

        if Command.DEFS in self.args:
            del self.args[Command.DEFS]

    def run(self):
        '''run the command and return result'''
        return Result("")

    def get(self, name, default=None):
        '''return var name from vars if set, otherwise return default'''
        var = self.vars.get(name, default)

        if var is None:
            return var

        try:
            return json.loads(var)
        except ValueError:
            if STRICT_MODE:
                raise
            else:
                return var

    def set(self, name, value):
        '''set var name to vars'''
        self.vars[name] = json.dumps(value)

    @classmethod
    def invoke(cls, data):
        '''invoke the command with *data* as input'''
        args = data.get("args", {})
        vars_ = data.get("vars", os.environ)

        instance = cls(args, vars_)

        try:
            return instance.run()
        except Exception as ex:
            if DEBUG:
                raise
            else:
                return Result.from_exception(ex)

    def get_args(self):
        '''get args if there are some otherwise get them from stdin

        if the only args are default args return them as a list'''

        if self.defs is not None and len(self.args) == 0:
            return self.defs
        elif len(self.args):
            return self.args
        else:
            return json.load(sys.stdin)

    def get_default_args(self):
        '''get the default arguments from vars if set if not get them from
        stdin'''

        if self.defs is not None:
            return self.defs
        else:
            return json.load(sys.stdin)

    def get_args_list(self, listify_item=False,
            return_single_flag=False, use_defaults_if_available=True):
        '''get the default arguments from vars if set if not get them from
        stdin

        if listify_item is True return a single item as a list

        if return_single_flag is True return a two item tuple with the second
        item being a flag signaling if args was originally a single item'''

        if use_defaults_if_available and self.defs is not None:
            defs = self.defs
        else:
            defs = json.load(sys.stdin)

        if listify_item:
            msg = "expected list or single item, got: %s"
        else:
            msg = "expected list, got: %s"


        single = False

        if isinstance(defs, dict):
            raise ValueError(msg % str(defs))
        elif not isinstance(defs, list):
            single = True
            defs = [defs]

        if return_single_flag:
            result = defs, single
        else:
            result = defs

        return result

    @classmethod
    def parse_args(cls, args):
        '''parse command line args and return a dict object with the options'''
        vals = {Command.DEFS: None}

        last_arg = Command.DEFS

        def add_option(arg, val):
            '''
            add the current *val* to arg
            arg can be a string or a list of strings
            '''

            if (val.isalnum() and val[0].isalpha() and
                    not val in ("true", "false", "null")):
                value = val
            else:
                try:
                    value = json.loads(val)
                except ValueError:
                    if STRICT_MODE:
                        raise
                    else:
                        value = val

            if isinstance(arg, list):
                for long_option in arg:

                    if isinstance(vals[long_option], list):
                        vals[long_option].append(value)
                    else:
                        vals[long_option] = [value]
            else:
                if arg in vals:
                    if vals[arg] is None:
                        vals[arg] = []

                    vals[arg].append(value)
                else:
                    vals[arg] = [value]

        for arg in args:

            if arg == "--":
                last_arg = Command.DEFS
            elif arg.startswith("--"):
                last_arg = arg[2:]
                vals[last_arg] = []

            elif arg.startswith("-"):

                # TODO: negative float
                if arg[1:].isdigit():
                    add_option(last_arg, arg)
                else:
                    last_arg = []

                    for letter in arg[1:]:
                        long_option = cls.EXPAND_SHORT_OPTIONS.get(letter,
                                letter)
                        last_arg.append(long_option)
                        vals[long_option] = True

            else:
                add_option(last_arg, arg)

        if vals[Command.DEFS] is None:
            del vals[Command.DEFS]

        result = {}
        for key, val in vals.iteritems():
            if isinstance(val, list) and len(val) == 1:
                result[key] = val[0]
            else:
                result[key] = val

        return result

    def get_arg_type(self, key, type_, default=None, name=None):
        '''try to get self.args[key], check if it's type *type_* if not raise
        ValueError if not found return default'''
        return util.expect_arg_type(self.args, key, type_, default, name)
