'''
This file is part of python-libdeje.

python-libdeje is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python-libdeje is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python-libdeje.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import print_function, absolute_import

from deje.protocol.handler      import ProtocolHandler
from deje.protocol.action       import ActionHandler
from deje.protocol.locking      import LockingHandler
from deje.protocol.retrieve     import RetrieveHandler
from deje.protocol.subscription import SubscriptionHandler

class DejeHandler(ProtocolHandler):
    def __init__(self, parent):
        ProtocolHandler.__init__(self, parent)
        self._on_action   = ActionHandler(self)
        self._on_lock     = LockingHandler(self)
        self._on_retrieve = RetrieveHandler(self)
        self._on_sub      = SubscriptionHandler(self)

    def _on_error(self, msg, content, ctype, doc):
        sender = msg.sender
        try:
            sender = self.owner.identities.find_by_location(sender).name
        except KeyError:
            pass # No saved information on this ident
        print("Error from %r, code %d: %r" % (sender, content['code'], content['explanation']))
