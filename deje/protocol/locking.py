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

from persei import *

from deje.protocol.handler import ProtocolHandler
from deje.action import Action

class LockingHandler(ProtocolHandler):

    def __init__(self, parent):
        ProtocolHandler.__init__(self, parent)

    def _on_acquire(self, msg, content, ctype, doc):
        lcontent = content['content']
        action = Action(lcontent, self.owner.identities).specific()
        quorum = doc._qs.get_quorum(action)
        if action.valid(doc):
            # TODO: Error message for validation failures
            quorum.sign(self.owner.identity)
            quorum.transmit(doc)
            quorum.check_enact(doc)

    def _on_acquired(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(content['signer'])
        action = Action(content['content'], self.owner.identities).specific()
        content_hash = String(action.hash())
        quorum = doc._qs.get_quorum(action)

        sig = RawData(content['signature'])
        quorum.sign(sender, sig)
        quorum.check_enact(doc)

    def _on_complete(self, msg, content, ctype, doc):
        action = Action(content['content'], self.owner.identities).specific()
        content_hash = String(action.hash())
        quorum = doc._qs.get_quorum(action)
        for signer in content['signatures']:
            sender = self.owner.identities.find_by_location(signer)
            sig = RawData(content['signatures'][signer])
            quorum.sign(sender, sig)
        quorum.check_enact(doc)
