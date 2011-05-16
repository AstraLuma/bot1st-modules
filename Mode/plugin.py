###
# Copyright (c) 2007, James Bliss
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
import sys; sys.path.append('/home/bot1st')
import supybot.utils as utils
from supybot.commands import *
from wrap2 import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.log import getPluginLogger
import time


class ChanData(object):
    threaded = True
    __slots__ = 'bans', 'listingbans', \
                'invites', 'listinginvites', \
                'excepts', 'listingexcepts', 
    def __init__(self):
        super(ChanData, self).__init__()
        self.bans = {}
        self.listingbans = False
        self.invites = {}
        self.listinginvites = False
        self.excepts = {}
        self.listingexcepts = False

class Mode(callbacks.Plugin):
    """Displays the channel mode"""
    _log = getPluginLogger('Mode')
    def __init__(self, irc):
        callbacks.Plugin.__init__(self, irc)
        self.channels = {}
        for channel in irc.state.channels.keys():
            self.__reloadLists(irc, channel)
    
    def __reloadLists(self, irc, channel):
        msg = ircmsgs.mode(channel, ['+beI'])
        irc.queueMsg(msg)
    
    def __getChannel(self, c):
        if c in self.channels:
            return self.channels[c]
        else:
            d = ChanData()
            self.channels[c] = d
            return d
    
    @wrap(["channel"])
    def showmode(self, irc, msg, args, channel):
        """[<channel>]
        
        Lists channel modes.
        """
#        channel = msg.args[0]
        modes = irc.state.channels[channel].modes
        rv = "+"
        for k,v in modes.items():
            rv += k
            if v is not None:
                rv += " "+v+" "
        irc.reply(rv)
    
    @wrap(["channel"])
    def bans(self, irc, msg, args, channel):
        """[<channel>]
        
        Lists channel bans.
        """
        #bans = irc.state.channels[channel].bans
        bans = self.__getChannel(channel).bans.keys()
        rv = ', '.join(bans)
        if len(bans) == 0:
            rv = "There are no bans"
        irc.reply(rv)
    
    @wrap(["channel"])
    def invites(self, irc, msg, args, channel):
        """[<channel>]
        
        Lists channel invites.
        """
        invites = self.__getChannel(channel).invites.keys()
        rv = ', '.join(invites)
        if len(invites) == 0:
            rv = "There are no invites"
        irc.reply(rv)
    
    @wrap(["channel"])
    def exceptions(self, irc, msg, args, channel):
        """[<channel>]
        
        Lists channel exceptions.
        """
        excepts = self.__getChannel(channel).excepts.keys()
        rv = ', '.join(excepts)
        if len(excepts) == 0:
            rv = "There are no exceptions"
        irc.reply(rv)
    
    @wrap(["channel"])
    def update(self, irc, msg, args, channel):
        """[<channel>]
        
        Updates channel lists.
        """
        self.__reloadLists(irc, channel)
        irc.replySuccess()
    
#    @wrap()
#    def test(self, irc, msg, args):
#        """
#        """
#        irc.reply(repr(msg))
    
    #RPL_BANLIST
    def do367(self, irc, msg):
        #self._log.info("Banlist: "+repr(msg))
        if len(msg.args) > 3:
            (_, channel, mask, op, time) = msg.args
        else:
            (_, channel, mask) = msg.args
            op = time = None
        chan = self.__getChannel(channel)
        if not chan.listingbans:
            chan.bans.clear()
            chan.listingbans = True
        chan.bans[mask] = (op, time)
    #RPL_ENDOFBANLIST
    def do368(self, irc, msg):
        (_, channel, _) = msg.args
        chan = self.__getChannel(channel)
        chan.listingbans = False

    #RPL_INVITELIST
    def do346(self, irc, msg):
        if len(msg.args) > 3:
            (_, channel, mask, op, time) = msg.args
        else:
            (_, channel, mask) = msg.args
            op = time = None
        chan = self.__getChannel(channel)
        if not chan.listinginvites:
            chan.invites.clear()
            chan.listinginvites = True
        chan.invites[mask] = (op, time)
    #RPL_ENDOFINVITELIST
    def do347(self, irc, msg):
        (_, channel, _) = msg.args
        chan = self.__getChannel(channel)
        chan.listinginvites = False

    #RPL_EXCEPTLIST
    def do348(self, irc, msg):
        if len(msg.args) > 3:
            (_, channel, mask, op, time) = msg.args
        else:
            (_, channel, mask) = msg.args
            op = time = None
        chan = self.__getChannel(channel)
        if not chan.listingexcepts:
            chan.excepts.clear()
            chan.listingexcepts = True
        chan.excepts[mask] = (op, time)
    #RPL_ENDOFEXCEPTLIST
    def do349(self, irc, msg):
        (_, channel, _) = msg.args
        chan = self.__getChannel(channel)
        chan.listingexcepts = False
    
    # We use RPL_TOPIC to update our ban list (primarily because it's sent when
    # we join a channel)
    def do332(self, irc, msg):
        (_, channel, _) = msg.args
        self.__reloadLists(irc, channel)
    # RPL_NOTOPIC, too
    do331 = do332
    
    # MODE message when other users change the mode
    def doMode(self, irc, msg):
        t = time.time()
        #self._log.info(repr(msg))
        channel = msg.args[0]
        chan = self.__getChannel(channel)
        modeLists = {'b':chan.bans, 'e':chan.excepts, 'I':chan.invites}
        for (mode, value) in ircutils.separateModes(msg.args[1:]):
            (action, modeChar) = mode
            if modeChar in 'beI':
                md = modeLists[modeChar]
                if action == '-' and value in md:
                    del md[value]
                elif action == '+':
                    md[value] = (msg.prefix, t)
Class = Mode


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
