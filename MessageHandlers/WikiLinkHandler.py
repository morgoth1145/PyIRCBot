import posixpath
import re

from .MessageHandlerBase import MessageHandlerBase

def get_all_links(site, message):
    output = []
    for link,template in re.findall('\[\[(.*?)(?:\|.*?)?\]\]|\{\{(.*?)(?:\|.*?)?\}\}', message):
        if link:
            output.append(posixpath.join(site,
                                         link.replace(' ', '_')))
        elif template:
            output.append(posixpath.join(site,
                                         'Template:'+template.replace(' ', '_')))
    return output

class WikiLinkHandler(MessageHandlerBase):
    def __init__(self, chan_name, site):
        MessageHandlerBase.__init__(self, chan_name)
        self.site = site

    def try_default(self, c, e):
        links = get_all_links(self.site, e.arguments[0])
        if 0 != len(links):
            c.privmsg(self.chan_name,
                      '%s meant: %s' % (e.source.nick,
                                        ', '.join(links)))
            return True
