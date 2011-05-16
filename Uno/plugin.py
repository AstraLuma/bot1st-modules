###
# Copyright (c) 2009, James Bliss
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
from wrap2 import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import random, re

HANDSIZE = 7

def gendeck():
    for c in 'rbgy':
        for n in xrange(0, 10):
            yield "%s%i" % (c, n)
            if n != 0:
                yield "%s%i" % (c, n)
        for s in 'srd':
            yield c+s
            yield c+s
    for n in xrange(4):
        yield 'w'
        yield 'w4'

PRNG = random.SystemRandom()

_ISCARD = re.compile('[rgby][0-9srd]|w4?', re.I)
def iscard(card):
    return bool(_ISCARD.match(card))

class UnoGame(object):
    def __init__(self):
        self.players = []
        self.hands = {}
        self.discard = []
        self.deck = list(gendeck())
        self.shuffle()
        self.curplayer = 0
        self.color = None
        self.number = None
    
    def shuffle(self):
        if self.discard:
            # Mix in discarded cards, except the top one
            self.deck += self.discard[:-1]
            del self.discard[:-1]
        PRNG.shuffle(self.deck)
    
    def draw(self, irc):
        if not self.deck:
            self.shuffle()
        return self.deck.pop()
    
    def deal(self, irc):
        try:
            for p in self.players:
                self.hands[p] = [self.draw(irc) for n in range(HANDSIZE)]
        except IndexError:
            irc.error("Out of cards")
    
    def isvalidplay(self, card):
        return (card[0] == 'w') or \
            (card[0] == self.color) or \
            (card[1] == self.number)
    
    def play(self, irc, card, color=None):
        self.discard.append(card)
        self.color = card[0]
        if self.color == 'w':
            self.color = color
            self.number = '*'
        else:
            self.number = card[1]
    
    def currentplayer(self):
        return self.players[0]
    
    def advanceplayer(self):
        """
        Returns the new current player.
        """
        lp = self.players[0]
        del self.players[0]
        self.players.append(lp)
        return self.players[0]
    
    def reverseplayers(self):
        cp = self.players[0]
        del self.players[0]
        self.players.reverse()
        self.players.insert(0, cp)
        

class Uno(callbacks.Plugin):
    """
    Will mediate a game of Uno. Inspired by an mIRC script.
    
    Card codes: Color followed by card.
    Cards:
    0-9: numbers
    r: reverse
    s: skip
    d: draw 2
    w: wild
    w4: wild, draw 4
    """
    
    #TODO: Use hostmasks internally?
    
    def __init__(self, irc):
        self.games = {}
        super(Uno, self).__init__(irc)
    
    def newturn(self, irc, channel):
        """
        1. Advances the current player
        2. Announces the current player and top card to channel
        3. Tells current player his hand
        """
        game = self.games[channel]
        # Step 1
        cp = game.advanceplayer()
        # Step 2
        topcard = game.discard[-1]
        if topcard[0] == 'w':
            topcard += ', current color is %s' % game.color
        irc.reply("Your turn, top card is %s" % topcard, to=cp, private=False)
        # Step 3
        irc.reply("Your hand is %s" % ', '.join(sorted(game.hands[cp])),
            to=cp, private=True, notice=True)
    
    def drawsome(self, irc, channel, player, n):
        """
        1. Draws some cards
        2. Gives cards to player
        3. Tells him what he drew
        """
        game = self.games[channel]
        cards = [game.draw(irc) for x in range(n)]
        game.hands[player] += cards
        irc.reply("You drew %s" % ', '.join(cards), to=player, private=True, notice=True)
    
    @wrap(["channel", "public"])
    def newgame(self, irc, msg, args, channel):
        """[<channel>]
        
        Starts a game of uno.
        """
        self.games[channel] = UnoGame()
        irc.replySuccess()
    
    @wrap(["channel", "public"])
    def end(self, irc, msg, args, channel):
        """[<channel>]
        
        Ends a game of uno
        """
        if channel not in self.games:
            irc.error("There is no game running")
            return
        #TODO: Print some kind of summary
        del self.games[channel]
        irc.replySuccess()
        
    @wrap(["channel"])
    def remove(self, irc, msg, args, channel):
        """[<channel>]
        
        Remove yourself from the current game
        """
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if nick not in game.players:
            irc.error("You're not playing")
            return
        game.players.remove(nick)
        if nick in game.hands:
            cards = game.hands[nick]
            del game.hands[nick]
            game.deck += cards
            game.shuffle()
        irc.replySuccess()
    
    @wrap(["channel"])
    def join(self, irc, msg, args, channel):
        """[<channel>]
        
        Type in the channel to reserve your spot in the game
        """
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if nick in game.players:
            irc.error("Already joined")
            return
        game.players.append(nick)
        irc.reply("You are player number %i" % len(game.players))
        if game.hands:
            # Already started
            game.hands[nick] = []
            if game.numdraws == 0:
                irc.reply("Keep drawing, no passes", to=nick, private=True)
            else:
                irc.reply("Draw %i, then pass" % game.numdraws, to=nick, private=True)
            self.drawsome(irc, channel, nick, HANDSIZE)
    
    @wrap(["channel", 'public'])
    def deal(self, irc, msg, args, channel):
        """[<channel>]
        
        Start a game
        """
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        game.deal(irc)
        #TODO: Shuffle players?
        card = game.draw(irc)
        while card[0] == 'w':
            game.play(irc, card)
            card = game.draw(irc)
        game.play(irc, card)
        PRNG.shuffle(game.players)
        game.numdraws = PRNG.randint(0,4)
        if game.numdraws == 0:
            irc.reply("Keep drawing, no passes", to=channel)
        else:
            irc.reply("Draw %i, then pass" % game.numdraws, to=channel)
        self.newturn(irc, channel)
    
    #TODO: user tracking and updating
    def doPart(self, irc, msg):
        pass
    
    def doQuit(self, irc, msg):
        pass
    
    def doNick(self, irc, msg):
        pass
    
    @wrap(["channel", "lowered", optional('something'), 'public'])
    def play(self, irc, msg, args, channel, card, color=None):
        """[<channel>] <card> [<color>]
        
        Play a card. Matches the regex /[rgby][0-9srd]|w4?/i
        If a wild is played, must give a color as well.
        """
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if nick not in game.players:
            irc.error("You're not playing")
            return
        if not game.hands:
            irc.error("Not yet playing")
            return
        #Check if it's their turn
        if not game.currentplayer() == nick:
            irc.error("You're not the current player")
            return
        #Verify it is a real card
        if not iscard(card):
            irc.error("Not a valid card")
            return
        #if it's a wild, make sure they gave a color
        if card[0] == 'w' and not (color and color[0].lower() in 'rgby'):
            irc.error("Must give a color as well")
            return
        elif card[0] == 'w':
            color = color[0].lower()
        #Verify that the card they played is a valid play
        if not game.isvalidplay(card):
            irc.error("Not valid play")
            return
        # Play the card, manipulate UnoGame
        try:
            game.hands[nick].remove(card)
        except:
            irc.error("You don't have that card")
            return
        game.play(irc, card, color)
        #Apply logic (draw, wild, skip, reverse)
        if card == 'w4':
            # Wild draw 4
            skipped = game.advanceplayer()
            self.drawsome(irc, channel, skipped, 4)
            irc.reply("You drew 4 and were skipped", to=skipped)
        elif card == 'w':
            # Handled, just don't want it to fall through
            pass
        elif card[1] == 's':
            # skip
            skipped = game.advanceplayer()
            irc.reply("You were skipped", to=skipped)
        elif card[1] == 'r':
            # Reverse
            game.reverseplayers()
        elif card[1] == 'd':
            # draw 2
            skipped = game.advanceplayer()
            self.drawsome(irc, channel, skipped, 2)
            irc.reply("You drew 2 and were skipped", to=skipped)
        if len(game.hands[nick]) == 1:
            irc.reply("UNO!", private=False)
        elif len(game.hands[nick]) == 0:
            irc.reply("%s wins" % nick, private=False, to=channel)
            del self.games[channel]
            return # Skip the new turn routine
        #Start new turn
        self.newturn(irc, channel)
    
    @wrap(["channel", 'public'])
    def draw(self, irc, msg, args, channel):
        """[<channel>]
        
        Draws a card from the deck if you cannot match the top card
        """
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if nick not in game.players:
            irc.error("You're not playing")
            return
        self.drawsome(irc, channel, nick, 1)
        irc.noReply()
    
    @wrap(["channel", 'public'])
    def _pass(self, irc, msg, args, channel):
        """[<channel>]
        
        If you cannot match the top card after you draw a card from the deck, 
        you must type pass
        """
        # If PRIVATE, print to public that he's skipping 
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if nick not in game.players:
            irc.error("You're not playing")
            return
        #TODO: Add permissions of some kind?
#        if not game.currentplayer() == nick:
#            irc.error("You're not the current player")
#            return
        self.newturn(irc, channel)
    locals()['pass'] = _pass
    
    @wrap(["channel"])
    def count(self, irc, msg, args, channel):
        """[<channel>]
        
        Displays the amount of cards in each players hand
        """
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        hands = game.hands
        if hands:
            msg = ', '.join('%s: %i' % (n, len(hands[n])) for n in sorted(hands))
        else:
            msg = "%i players but not dealt" % len(game.players)
        irc.reply(msg)
        
    
    @wrap(["channel"])
    def order(self, irc, msg, args, channel):
        """[<channel>]
        
        Displays players in order by turn
        """
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        irc.reply(', '.join(game.players))

    @wrap(["channel"])
    def top(self, irc, msg, args, channel):
        """[<channel>]
        
        Show the top card
        """
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if not game.hands:
            irc.error("Not yet playing")
            return
        topcard = game.discard[-1]
        if topcard[0] == 'w':
            topcard += ', current color is %s' % game.color
        irc.reply("The top card is %s" % topcard)
    
    @wrap(["channel"])
    def hand(self, irc, msg, args, channel):
        """[<channel>]
        
        Show your hand
        """
        nick = msg.nick
        if channel not in self.games:
            irc.error("There is no game running")
            return
        game = self.games[channel]
        if nick not in game.players:
            irc.error("You're not playing")
            return
        if not game.hands:
            irc.error("Not yet playing")
            return
        irc.reply("Your hand is %s" % ', '.join(sorted(game.hands[nick])),
            to=nick, private=True, notice=True)
    
Class = Uno


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
