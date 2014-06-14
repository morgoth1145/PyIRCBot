import posixpath

from .MessageHandlerBase import MessageHandlerBase

class WikiStatsHandler(MessageHandlerBase):
    def __init__(self, chan_name, site):
        MessageHandlerBase.__init__(self, chan_name)

        stats = self.options.add_option('!stats')
        stats.add_option('links').action = WikiStatsHandler.stats(site,
                                                                  'WhatLinksHere')
        stats.add_option('prefix').action = WikiStatsHandler.stats(site,
                                                                   'PrefixIndex')
        stats.add_option('contribs').action = WikiStatsHandler.stats(site,
                                                                     'Contributions')
        stats.add_option('edits').action = WikiStatsHandler.stats(site,
                                                                  'EditCount')

    @staticmethod
    def stats(site, stat_type):
        url_begin = posixpath.join(site, 'Special:'+stat_type)
        def inner(self, c, e, rem_args):
            links = [posixpath.join(url_begin, item.replace(' ', '_'))
                     for item
                     in rem_args]
            if 0 != len(links):
                c.privmsg(self.chan_name,
                          '%s requested: %s' % (e.source.nick,
                                                ', '.join(links)))
                return True
        return inner
