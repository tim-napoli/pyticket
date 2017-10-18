"""
Command line management.
"""
import inspect

class argument:
    def __init__(self, name, description, optional):
        self.name = name
        self.description = description
        self.optional = optional

    def usage(self):
        print("        {} {} {}".format(
            self.name, "(optional)" if self.optional else "", self.description
        ))

class command:
    def __init__(self, name, description, callback = None):
        self.name = name
        self.description = description
        self.callback = callback
        self.args = command.__args_of_callback(callback) if callback else []

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
                raise Exception(
                    "only 'None' default parameter value is authorized for "
                    "commands callbacks"
                )
            optional = arg.default == None
            args += [argument(arg.name, doc, optional)]
        return args

    def try_execute(self, argv):
        if argv[0] != self.name:
            return False
        if self.callback == None:
            raise Exception(
                "command '{}' is not implemented".format(self.name)
            )
        current_arg = 0
        args = {}
        for arg_str in argv[1:]:
            if current_arg == len(self.args):
                break
            args[self.args[current_arg].name] = arg_str
            current_arg = current_arg + 1
        if (current_arg < len(self.args)
                and not self.args[current_arg].optional):
            raise Exception(
                "missing argument '{}' for command '{}'".format(
                    self.args[current_arg].name, self.name
                )
            )
        rest = argv[1 + current_arg:]
        self.callback(rest, **args)
        return True

    def usage(self):
        def do_arg_str(arg):
            return ("[" + arg.name + "]" if arg.optional
                    else "<" + arg.name + ">")
        args_str = " ".join([do_arg_str(arg) for arg in self.args])
        print("    {} {} {}".format(self.name, args_str, self.description))
        for arg in self.args:
            arg.usage()


def print_usage(prg_name, commands):
    print("{} <command> <args...>".format(prg_name))
    for cmd in commands:
        cmd.usage()

def execute_argv(commands, argv):
    for cmd in commands:
        if cmd.try_execute(argv):
            return
    raise Exception("command '{}' is not valid".format(argv[0]))

