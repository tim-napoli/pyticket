"""
Command line management.
"""
import inspect
from pyticket import PyticketException

class argument:
    def __init__(self, name, description, optional):
        self.name = name
        self.description = description
        self.optional = optional

    def usage(self):
        print("        {} {} {}".format(
            self.name, "(optional)" if self.optional else "", self.description
        ))

class option:
    def __init__(self, name, description, has_arg):
        self.name = name
        self.description = description
        self.has_arg = has_arg

    def usage(self):
        print("        --{} {} {}".format(
            self.name, "<arg>" if self.has_arg else "", self.description
        ))

class command:
    def __init__(self, name, description, callback = None, options = []):
        self.name = name
        self.description = description
        self.callback = callback
        self.args = command.__args_of_callback(callback) if callback else []
        self.options = options

    @staticmethod
    def __args_of_callback(callback):
        parameters = inspect.signature(callback).parameters
        annotations = callback.__annotations__
        args = []
        for arg in parameters.items():
            arg = arg[1]
            if not arg.name in annotations:
                continue
            doc = annotations[arg.name]
            if (arg.default != inspect._empty
                    and arg.default != None):
                raise PyticketException(
                    "only 'None' default parameter value is authorized for "
                    "commands callbacks"
                )
            optional = arg.default == None
            args += [argument(arg.name, doc, optional)]
        return args

    def find_option(self, name):
        for opt in self.options:
            if opt.name == name:
                return opt
        return None

    def parse_options(self, argv):
        def is_option(arg):
            return arg.startswith("--")
        options = {}
        current_opt = 0
        while current_opt < len(argv):
            arg = argv[current_opt]
            if is_option(arg):
                opt = self.find_option(arg[2:])
                if not opt:
                    raise PyticketException(
                        "command '{}' has no option called '{}'".format(
                            self.name, arg[2:]
                        )
                    )
                opt_arg = None
                if opt.has_arg:
                    if (current_opt + 1 == len(argv) or
                            is_option(argv[current_opt + 1])):
                        raise PyticketException(
                            "option '{}' needs a parameter".format(opt.name)
                        )
                    opt_arg = argv[current_opt + 1]
                    current_opt = current_opt + 1
                options[opt.name] = opt_arg
                current_opt = current_opt + 1
            else:
                raise PyticketException("unexpected token '{}'".format(opt))
        return options

    def try_execute(self, argv):
        if argv[0] != self.name:
            return False
        if self.callback == None:
            raise PyticketException(
                "command '{}' is not implemented".format(self.name)
            )
        current_arg = 0
        args = {}
        for arg_str in argv[1:]:
            if current_arg == len(self.args) or arg_str.startswith("--"):
                break
            args[self.args[current_arg].name] = arg_str
            current_arg = current_arg + 1
        if (current_arg < len(self.args)
                and not self.args[current_arg].optional):
            raise PyticketException(
                "missing argument '{}' for command '{}'".format(
                    self.args[current_arg].name, self.name
                )
            )
        rest = argv[1 + current_arg:]
        options = self.parse_options(rest)
        self.callback(options, **args)
        return True

    def usage(self):
        def do_arg_str(arg):
            return ("[" + arg.name + "]" if arg.optional
                    else "<" + arg.name + ">")
        args_str = " ".join([do_arg_str(arg) for arg in self.args])
        print("    {} {} {}".format(self.name, args_str, self.description))
        if self.args:
            print("      arguments:")
            for arg in self.args:
                arg.usage()
        if self.options:
            print("      options:")
            for opt in self.options:
                opt.usage()


def print_usage(prg_name, commands):
    print("{} <command> <args...>".format(prg_name))
    for cmd in commands:
        print("")
        cmd.usage()

def execute_argv(commands, argv):
    for cmd in commands:
        if cmd.try_execute(argv):
            return
    raise PyticketException("command '{}' is not valid".format(argv[0]))

