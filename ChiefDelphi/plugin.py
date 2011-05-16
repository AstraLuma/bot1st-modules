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
import re, htmlentitydefs
from supybot.log import getPluginLogger

_entsRe = re.compile(r'&([^&;\s]+);', re.L | re.U)
def _replaceEnts(txt):
    pass

class ChiefDelphi(callbacks.Plugin):
    """Commands related to ChiefDelphi. Nothing fancy."""
    threaded = True
    
    _cdqRe = re.compile(r'document.write\("(.*)"\);', re.I | re.U)
    _cdqUrl = "http://www.chiefdelphi.com/forums/xml/spotlight_js.php"
    _log = getPluginLogger('ChiefDelphi')
    @wrap()
    def cdq(self, irc, msg, args):
        """takes no arguments

        Shows a ChiefDelphi spotlight. Can be called as "cdq" or "spotlight"
        """
        try:
            script = utils.web.getUrl(self._cdqUrl,headers={'User-agent':'#firstrobotics bot1st (operated by astronouth7303)'})
        except Error, err:
            irc.replyError("Couldn't load quote")
            return
        m = self._cdqRe.match(script)
        if m is None:
            irc.replyError("Couldn't parse quote")
            return
        text = m.group(1)
        self._log.info(repr(text))
        quote = text.decode('string_escape')
        # TODO: Add HTML entity decoding
        
        irc.reply(quote)
    spotlight=cdq


Class = ChiefDelphi


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
