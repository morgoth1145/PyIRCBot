from .MessageHandlerBase import MessageHandlerBase

class CharHandler(MessageHandlerBase):
    def __init__(self, chan_name, char_manager):
        super().__init__(chan_name)
        self.char_manager = char_manager

        rp = self.options.add_option('rp')
        char = rp.add_option('char')
        char.add_option('add').action = CharHandler.add_char
        char.add_option('drop').action = CharHandler.drop_char
        char.add_option('list').action = CharHandler.list_char

    def add_char(self, c, e, rem_args):
        if 1 != len(rem_args):
            return False
        self.char_manager.add(rem_args[0])
        c.privmsg(self.chan_name, 'Character added: %s' % rem_args[0])
        return True

    def drop_char(self, c, e, rem_args):
        if 1 != len(rem_args):
            return False
        self.char_manager.remove(rem_args[0])
        c.privmsg(self.chan_name, 'Character removed: %s' % rem_args[0])
        return True

    def list_char(self, c, e, rem_args):
        if 0 != len(rem_args):
            return False
        c.privmsg(self.chan_name, 'Known characters:')
        for char in self.char_manager.chars:
            c.privmsg(self.chan_name, '\t%s' % char)
        return True
