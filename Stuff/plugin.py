###
# Copyright (c) 2006, Jamie Bliss
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
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import random, re, subprocess
import math, time
import urllib

ACTIONS = [
    'loading...',
    'extracting...',
    'shaking...',
    'liquefying bytes...',
    'homogenizing goo...',
    'testing ozone...',
    'processing...',
    'spinning violently around the y-axis...',
    'iodizing...',
    'stretching images...',
    'reconstituting sounds...',
    'faithfully re-imagining...',
    'scraping funds...',
    'applying innovation...',
    'constructing emotional depth...',
    'debating games as art...',
    'placating publishers...',
    'meticulously diagramming fun...',
    'filtering moral...',
    'testing for perfection...',
    'revolving independence...',
    'tokenizing innovation...',
    'self affirming...',
    'dissolving relationships...',
    'deterministically simulating the future...',
    'exceeding cpu quota...',
    'swapping time and space...',
    'embiggening prototypes...',
    'sandbagging expectations...',
    'challenging everything...',
    'distilling beauty...',
    'blitting powers of two...',
    'manufacturing social responsibility...',
    'bending the spoon...',
    'constructing non-linear narrative...',
    ]

#def factorize(n):
#    def isPrime(n):
#        return not [x for x in xrange(2,int(math.sqrt(n)))
#                    if n%x == 0]
#    primes = []
#    candidates = xrange(2,n+1)
#    candidate = 2
#    while not primes and candidate in candidates:
#        if n%candidate == 0 and isPrime(candidate):
#            primes = primes + [candidate] + factorize(n/candidate)
#        candidate += 1            
#    return primes

def factorize(n):
    if n == 0 or n == 1: return []
    f = 2
    s = math.sqrt(n) + 1
    while n%f != 0:
        if f > s: return [n]
        f += 1
    else:
        return [f]+factorize(n//f)    

class Stuff(callbacks.Plugin):
    """Provides some commands for #firstrobotics. (Don't ask!)
    """
    @wrap()
    def death(self, irc, msg, args):
        """takes no arguments"""
        if random.random() < 0.05:
            irc.reply('X-p', prefixNick=False)
        else:
            irc.reply('Death? What strange concepts you pitiful humans create.')
    
    @wrap()
    def ddate(self, irc, msg, args):
        """takes no arguments"""
        args = ['ddate']
        inst = subprocess.Popen(args, stdout=subprocess.PIPE)
        r = inst.stdout
        try:
            lines = r.readlines()
            lines = map(str.rstrip, lines)
            lines = filter(None, lines)
            if lines:
                irc.replies(lines, joiner=' ')
        finally:
            r.close()
            inst.wait()
    
    @wrap()
    def raptors(self, irc, msg, args):
        """takes no arguments"""
        channel = msg.args[0]
        if irc.nick in irc.state.channels[channel].ops:
            irc.queueMsg(ircmsgs.kick(channel, msg.nick, 'Raptor Attack!'))
            irc.reply( ("%(name)s just got attacked by several raptors.  As they " +
                    "pick the remaining meat from %(name)s's bones they look up " +
                    "and see BamaWOLF...")  % {'name': msg.nick}, prefixNick=False )
        else:
            irc.reply("runs screaming", action=True)
    
    _meRe = re.compile(r'\bme\b|\bb[o0]t[1\|]st\b|\bhimself\b|\bherself\b', re.I)
    _myRe = re.compile(r'\bmy\b', re.I)
    def _replaceFirstPerson(self, s, nick):
        s = self._meRe.sub(nick, s)
        s = self._myRe.sub('%s\'s' % nick, s)
        return s
    @wrap(['text'])
    def shutup(self, irc, msg, args, text):
        """<who> [for <reason>]

        Tells <who> to shutup.
        """
        def _firstWord(s):
            return s.split()[0]
        if ' for ' in text:
            (target, reason) = map(str.strip, text.split(' for ', 1))
        else:
            (target, reason) = (text, '')
        msgtext = "duct tapes $who"
        text = self._replaceFirstPerson(msgtext, msg.nick)
        if ircutils.strEqual(target, irc.nick) or ircutils.strEqual(_firstWord(target), irc.nick):
            target = msg.nick
            reason = self._replaceFirstPerson('trying to dis me', irc.nick)
        else:
            target = self._replaceFirstPerson(target, msg.nick)
            reason = self._replaceFirstPerson(reason, msg.nick)
        if target.endswith('.'):
            target = target.rstrip('.')
        text = text.replace('$who', target)
        if reason:
            text += ' for ' + reason
        irc.reply(text, action=True)

    @wrap(['text'])
    def misnick(self, irc, msg, args, text):
        """<who> [for <reason>]

        Expresses displeassure of a chosen nick
        """
        if ' for ' in text:
            (target, reason) = map(str.strip, text.split(' for ', 1))
        else:
            (target, reason) = (text, '')
        msgtext = "smacks $who into oblivion"
        text = self._replaceFirstPerson(msgtext, msg.nick)
        if ircutils.strEqual(target, irc.nick):
            target = msg.nick
            reason = self._replaceFirstPerson('trying to dis me', irc.nick)
        else:
            target = self._replaceFirstPerson(target, msg.nick)
            reason = self._replaceFirstPerson(reason, msg.nick)
        if target.endswith('.'):
            target = target.rstrip('.')
        text = text.replace('$who', target)
        if reason:
            text += ' for ' + reason
        irc.reply(text, action=True)
    
    @wrap()
    def wow(self, irc, msg, args):
        """
        
        Retorts for ServerWOLF
        """
        irc.reply("gives ServerWOLF a towel to cover itself up with", action=True)
    
    @wrap()
    def pong(self, irc, msg, args):
        """ """
        irc.reply("hits the ping ball back at %s" % msg.nick,action=True)
    
    @wrap()
    def clearscreen(self, irc, msg, args):
        """ """
        for c in "CLEARTHESCREEN!":
            irc.reply(c, prefixNick=False)
    
    @wrap()
    def about(self, irc, msg, args):
        """
        
        Gives some information about the bot
        """
        irc.reply("""
I am ran by astronouth7303 <http://www.astro73.com/> and powered by supybot. For
information on usage, just say "!intro" (no quotes).
""".replace("\n", ' ').replace("  ", " ").strip())
    
    @wrap()
    def praxis(self, irc, msg, args):
        """
        
        Gives some information about the praxis
        """
        irc.reply("""
        Write an animal-like AI for the channel. I would like to see some kind of learning.
""".replace("\n", ' ').replace("  ", " ").strip())
    
    @staticmethod
    def factorfmt(b,n):
        if n == 1:
            return str(b)
        else:
            return '%i^%i' % (b, n)
    @wrap([additional(('int', 'number'), -1)])
    def factor(self, irc, msg, args, num):
        """[<number>]
        
        Factor a number or the current time. See <http://xkcd.com/247/>.
        """
        if num < 0:
            lt = time.localtime()
            hr, mn = lt[3:5]
            snum = "%i:%02i" % (hr, mn)
            num = int("%i%02i" % (hr,mn))
        else:
            snum = num
        factors = factorize(num)
        if len(factors) == 0:
            irc.reply("%s is mathematically ambiguous" % snum)
        elif len(factors) == 1:
            irc.reply("%s is prime" % snum)
        else:
            powers = [(factors[0], 1)]
            for n in factors[1:]:
                if n == powers[-1][0]:
                    powers[-1] = (powers[-1][0], powers[-1][1]+1)
                else:
                    powers.append((n, 1))
            irc.reply("%s factors into %s" % (snum, ' * '.join(self.factorfmt(*f) for f in powers)))
    
    @wrap()
    def ufactor(self, irc, msg, args):
        """
        
        Factor the current unix timestamp.
        """
        num = int(time.time())
        factors = factorize(num)
        if len(factors) == 0:
            irc.reply("Mathematically ambiguous")
        elif len(factors) == 1:
            irc.reply("%i is prime" % num)
        else:
            powers = [(factors[0], 1)]
            for n in factors[1:]:
                if n == powers[-1][0]:
                    powers[-1] = (powers[-1][0], powers[-1][1]+1)
                else:
                    powers.append((n, 1))
            def fmt(b,n):
                if n == 1:
                    return str(b)
                else:
                    return '%i^%i' % (b, n)
            irc.reply("Factors into %s" % (' * '.join(self.factorfmt(*f) for f in powers)))
    
    @wrap()
    def do(self, irc, msg, args):
        """
        
        Does something, possibly usefully.
        """
        irc.reply(random.choice(ACTIONS))
    
    NICE = False
    @wrap(['text'])
    def lmgtfy(self, irc, msg, args, q):
        """<stuff>
        
        Links to lmgtfy.com for lazy bastards to be snarky to lazy bastards
        """
        url = "http://lmgtfy.com/?q=%s" % urllib.quote(q)
        if self.NICE: # Says "It's that easy" instead of "Was that so hard"
            url += '&n=1'
        irc.reply(url)
    lmgt = lmgtfy

Class = Stuff

# vim:set shiftwidth=4 tabstop=4 expandtab:
