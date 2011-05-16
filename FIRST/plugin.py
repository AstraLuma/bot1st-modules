###
# Copyright (c) 2006, James Bliss
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import datetime, os, time

def utcnow():
    f = os.popen('date +%s')
    t = f.read()
    f.close()
    return int(t)
def formatstamp(ts):
    return "%i:%i:%i" % (ts // 60**2, ts // 60 % 60, ts % 60)

class FIRST(callbacks.Plugin):
    """Various commands for FIRST"""
    callBefore = ('Factoids', 'MoobotFactoids', 'Infobot', 'Karma')
    KICKOFF = datetime.datetime(2010, 1, 9, 10, 0, 0)
    SHIP = datetime.datetime(2010, 2, 23, 0, 0, 0)
    NATS = datetime.datetime(2010, 3, 4, 14, 0, 0)
    CALLS = {
        'GALI-': 'LEO!',
        'ARCHI-': 'MEDES!',
    }
    
    def _doResponse(self, irc, channel, thing):
        irc.reply(self.CALLS[thing], prefixNick=False)
    
    def invalidCommand(self, irc, msg, tokens):
        channel = msg.args[0]
        if not irc.isChannel(channel):
            return
        if tokens[-1].upper() in self.CALLS:
            self._doResponse(irc, channel, tokens[-1].upper())
    
    def doPrivmsg(self, irc, msg):
        # We don't handle this if we've been addressed because invalidCommand
        # will handle it for us.  This prevents us from accessing the db twice
        # and therefore crashing.
        if not (msg.addressed or msg.repliedTo):
            channel = msg.args[0]
            if irc.isChannel(channel):
                irc = callbacks.SimpleProxy(irc, msg)
                tokens = msg.args[1].split(' ')
                thing = tokens[-1]
                if thing.upper() in self.CALLS:
                    self._doResponse(irc, channel, thing.upper())
    
    def finddiff(self, irc, date):
        time.mktime(datetime.datetime(2010, 2, 23, 0, 0, 0).timetuple())
        delta = date - datetime.datetime.now()
        if delta.days < 0:
            delta = formatstamp(time.mktime(date.timetuple()) - utcnow())
        irc.reply(delta)
    
    @wrap()
    def kickoff(self, irc, msg, args):
        """(takes no args)
        
        displays the time left until kickoff."""
        self.finddiff(irc, self.KICKOFF)

    @wrap()
    def ship(self, irc, msg, args):
        """(takes no args)
        
        displays the time left until ship."""
        self.finddiff(irc, self.SHIP)

    @wrap()
    def nats(self, irc, msg, args):
        """(takes no args)
        
        displays the time left until kickoff."""
        self.finddiff(irc, self.NATS)

Class = FIRST


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
