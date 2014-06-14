import errno
import os

from .MessageHandlerBase import MessageHandlerBase

def ensure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        if not os.path.isdir(path):
            raise RuntimeError('Path exists, but not as a directory')

def dump(lines, filename):
    with open(filename, 'w+') as f:
        for line in lines:
            f.write(line + '\n')

def do_format(lines, characters):
    import re
    output = []
    cur = None
    for line in lines:
        m = re.match('(.*) \- (.*)', line)
        if m is not None:
            char = m.group(1)
            if char in characters:
                if cur is not None:
                    output.append(cur)
                    cur = None
                output.append("*'''%s''' - ''%s''" % (char, m.group(2)))
                continue
        if cur is None:
            cur = line
        else:
            cur += ' ' + line
    if cur is not None:
        output.append(cur)
    return output

class Buffer:
    def __init__(self):
        self.running = False

    def start(self):
        self.lines = []
        self.running = True

    def add(self, msg):
        if self.running:
            self.lines.append(msg)

    def stop(self, characters):
        if self.running:
            self.running = False
            dt = datetime.now()
            dt = '%02d-%02d-%02d %02d-%02d-%02d.%06d' % (dt.year,
                                                         dt.month,
                                                         dt.day,
                                                         dt.hour,
                                                         dt.minute,
                                                         dt.second,
                                                         dt.microsecond)
            ensure_path_exists('logs')
            dump(self.lines,
                 os.path.join('logs',
                              dt+' raw.log'))
            dump(do_format(self.lines, characters),
                 os.path.join('logs',
                              dt+' formatted.log'))

class RoleplayHandler(MessageHandlerBase):
    def __init__(self, chan_name, char_manager):
        MessageHandlerBase.__init__(self, chan_name)
        self.buffer = Buffer()
        self.char_manager = char_manager

        rp = self.options.add_option('rp')
        rp.add_option('begin').action = RoleplayHandler.begin_roleplay
        rp.add_option('finish').action = RoleplayHandler.finish_roleplay

    def begin_roleplay(self, c, e, rem_args):
        if 0 != len(rem_args):
            return False
        if self.buffer.running:
            c.privmsg(self.chan_name, 'Roleplay is already running!')
            return True
        self.buffer.start()
        c.privmsg(self.chan_name, 'Roleplay started.')
        return True

    def finish_roleplay(self, c, e, rem_args):
        if 0 != len(rem_args):
            return False
        if not self.buffer.running:
            c.privmsg(self.chan_name, 'No roleplay is running')
            return True
        self.buffer.stop(self.char_manager.chars)
        c.privmsg(self.chan_name, 'Roleplay ended.')
        return True

    def try_default(self, c, e):
        if self.buffer.running:
            self.buffer.add(e.arguments[0])
            return true
