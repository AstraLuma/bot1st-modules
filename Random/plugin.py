###
# Copyright (c) 2006, Daniel DiPaolo
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
import random

class Random(callbacks.Plugin):
    """This plugin provides a few random number commands and some
    commands for getting random samples.  Use the "seed" command to
    seed the plugin's random number generator if you like, though
    it is unnecessary as it gets seeded upon loading of the plugin.
    The "random" command is most likely what you're looking for,
    though there are a number of other useful commands in this
    plugin.  Use 'list random' to check them out.
    """
    def __init__(self, irc):
        self.__parent = super(Random, self)
        self.__parent.__init__(irc)
        self.rng = random.Random()   # create our rng
        self.rng.seed()   # automatically seeds with current time
    
    @wrap()
    def random(self, irc, msg, args):
        """takes no arguments

        Returns the next random number from the random number generator."""
        irc.reply(str(self.rng.random()))
    
    @wrap(['float'])
    def seed(self, irc, msg, args, seed):
        """<seed>

        Sets the internal RNG's seed value to <seed>.  <seed> must be a floating
        point number.
        """
        self.rng.seed(seed)
        irc.replySuccess()
    
    @wrap(['int', many('anything')])
    def sample(self, irc, msg, args, n, items):
        """<number of items> <item1> [<item2> ...]

        Returns a sample of the <number of items> taken from the remaining
        arguments.  Obviously <number of items> must be less than the number
        of arguments given.
        """
        if n > len(items):
            irc.error('<number of items> must be less than the number '
                      'of arguments.')
            return
        sample = self.rng.sample(items, n)
        sample.sort()
        irc.reply(utils.str.commaAndify(sample))

    @wrap([additional(('int', 'number of sides'), 6)])
    def diceroll(self, irc, msg, args, n):
        """[<number of sides>]

        Rolls a die with <number of sides> sides.  The default number of
        sides is 6.
        """
        s = 'rolls a %s' % self.rng.randrange(1, n)
        irc.reply(s, action=True)

Class = Random


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
