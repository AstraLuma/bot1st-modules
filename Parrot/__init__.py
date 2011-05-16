###
# Copyright (c) 2006, Benson Kalahar
# All rights reserved.
#
#
###

"""
Parrot is a plugin that will repeat back whatever is said by a given user.
It's designed to be very annoying.  (Ideally, it would be activated on a user
who is very annoying.)  
"""

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = "0.0.2"
__author__ = supybot.Author("Benson Kalahar", "bensonk", "bensonk@acm.org");
__contributors__ = {}
__url__ = 'http://acm.wwu.edu/~bensonk/supybot/' # 'http://supybot.com/Members/yourname/Parrot/download'

import config
import plugin
reload(plugin) # In case we're being reloaded.
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
	import test

Class = plugin.Class
configure = config.configure
