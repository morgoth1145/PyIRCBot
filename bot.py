import configparser
import textwrap
import threading

import irc.bot
import irc.client

class CharManager:
    def __init__(self):
        self.chars = list(c.strip() for c in open('characters'))
    def add(self, char):
        if char not in self.chars:
            self.chars.append(char)
            with open('characters', 'w+') as f:
                for c in self.chars:
                    f.write(c+'\n')
    def remove(self, char):
        if char in self.chars:
            self.chars.remove(char)
            with open('characters', 'w+') as f:
                for c in self.chars:
                    f.write(c+'\n')

class MyBot(irc.bot.SingleServerIRCBot):
    def __init__(self, *args, **kwargs):
        irc.bot.SingleServerIRCBot.__init__(self, *args, **kwargs)
        self.connection_checker_set = False

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + '_')

    def on_welcome(self, c, e):
        from MessageHandlers import CharHandler, RoleplayHandler, WikiLinkHandler, WikiStatsHandler

        orig_privmsg = c.privmsg
        def chunked_privmsg(target, text):
            for line in textwrap.wrap(text, 400-len(target)):
                orig_privmsg(target, line)
        c.privmsg = chunked_privmsg

        if not self.connection_checker_set:
            c.set_keepalive(self.reconnection_interval)
            c.execute_delayed(self.reconnection_interval,
                              self._connected_checker)
            self.connection_checker_set = True

        char_manager = CharManager()
        site = 'http://spore.wikia.com/wiki/'

        self.chan_name_to_handlers = {}
        for chan in self.channels_to_join:
            chan_name = chan[0]
            c.join(chan_name)
            self.chan_name_to_handlers[chan_name] = [CharHandler(chan_name, char_manager),
                                                     RoleplayHandler(chan_name, char_manager),
                                                     WikiLinkHandler(chan_name, site),
                                                     WikiStatsHandler(chan_name, site)]

    def on_pubmsg(self, c, e):
        handlers = self.chan_name_to_handlers[e.target]
        for h in handlers:
            if h.try_handle(c, e):
                return
        for h in handlers:
            if h.try_default(c, e):
                return

    # The SingleServerIRCBot implementation doesn't do this correctly
    def _connected_checker(self):
        if self.connection.is_connected():
            try:
                self.connection.ping(self.connection.server)
            except irc.client.ServerNotConnectedError:
                pass
        else:
            self.jump_server()
        self.connection.execute_delayed(self.reconnection_interval,
                                        self._connected_checker)
    def _on_disconnect(self, c, e):
        import irc.dict
        self.channels = irc.dict.IRCDict()
    def start(self):
        self._bot_exit = False
        while True:
            try:
                irc.bot.SingleServerIRCBot.start(self)
            except irc.client.ServerNotConnectedError:
                if not self._bot_exit:
                    continue
            break
    def die(self):
        self._bot_exit = True
        irc.bot.SingleServerIRCBot.die(self)

def ServerSpec(server):
    host,port = server.split('@')
    return irc.bot.ServerSpec(host, int(port))
def Channel(channel):
    return (channel,)

config = configparser.ConfigParser()
config.read('bot.ini')
server_list = [ServerSpec(server)
               for server
               in config['Connection']['servers'].split(';')]
channels = [Channel(chan)
            for chan
            in config['Connection']['channels'].split(';')]

nick = config['Identity']['nick']
realname = config['Identity']['realname']

bot = MyBot(server_list,
            nick,
            realname,
            reconnection_interval=15)
bot.channels_to_join = channels

class AsyncTask(threading.Thread):
    def __init__(self, task):
        threading.Thread.__init__(self)
        self.task = task
        self.result = None
    def run(self):
        self.result = self.task()
async_bot = AsyncTask(lambda: bot.start())

async_bot.start()
while True:
    command = input('What should I do? (exit to exit): ')
    if 'exit' == command:
        bot.die()
        async_bot.join()
        break
