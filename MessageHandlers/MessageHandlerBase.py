import shlex

class _CommandParser:
    def __init__(self, skip_help=False):
        self._options = {}
        self.action = None
        if not skip_help:
            opt = self.add_option('-h', True)
            options_closure = self._options
            def help_fn(self, c, e, rem_args):
                for opt_name in options_closure.keys():
                    if '-h' != opt_name:
                        c.privmsg(e.target, '\t%s' % opt_name)
            opt.action = help_fn
    def add_option(self, name, skip_help=False):
        opt = self._options[name] = _CommandParser(skip_help)
        return opt
    def try_parse(self, args):
        if self.action is not None:
            return self.action,args
        if 0 == len(args):
            return None,None
        opt = self._options.get(args[0])
        if opt is None:
            return None,None
        return opt.try_parse(args[1:])

class MessageHandlerBase:
    def __init__(self, chan_name):
        self.chan_name = chan_name
        self.options = _CommandParser()

    def try_handle(self, c, e):
        sender = e.source
        msg = e.arguments[0]

        try:
            args = shlex.split(msg)
        except ValueError:
            pass
        else:
            action,rem_args = self.options.try_parse(args)
            if action is not None:
                if action(self, c, e, rem_args):
                    return True

    def try_default(self, c, e):
        pass
