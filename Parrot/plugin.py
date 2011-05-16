###
# Copyright (c) 2006, Benson Kalahar
# All rights reserved.
#
# Relased under the GNU GPL
###

import re
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Parrot(callbacks.Plugin):
	"""To use parrot, simply call it with a nickname:
	@parrot tehJ
	"""

	def __init__(self, irc):
		self.__parent = super(Parrot, self)
		self.__parent.__init__(irc)
		self._targets = set()

	def add(self, irc, msg, args, user):
		"""<user>
		adds user to parrot list"""
		if ircutils.strEqual(user, irc.nick):
			irc.reply('No, I will not parrot myself.')
			return
		self._targets.add(user)
		irc.replySuccess()
	add = wrap(add, [('checkCapability', 'owner'), 'text'])

	def remove(self, irc, msg, args, user):
		"""<user>
		removes user from parrot list"""
		self._targets.remove(user)
		irc.replySuccess()
	remove = wrap(remove, [('checkCapability', 'owner'), 'text'])

	def targets(self, irc, msg, args):
		"""takes no arguments
		returns current list of targets"""
		if self._targets:
			irc.reply("Current targets: " + utils.str.commaAndify(self._targets))
		else:
			irc.reply("There are currently no targets.")
	targets = wrap(targets, [('checkCapability', 'owner')])

	def doPrivmsg(self, irc, msg):
		if msg.nick in self._targets:
			IAmRe = re.compile(r'I am', re.I)
			text = re.sub(IAmRe, msg.nick + " is", msg.args[1])
			irc.reply(text, prefixNick=False)

	def doNick(self, irc, msg):
		oldNick = msg.nick
		newNick = msg.args[0]
		if oldNick in self._targets:
			self._targets.remove(oldNick)
			self._targets.add(newNick)


Class = Parrot
