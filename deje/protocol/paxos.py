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

from __future__ import absolute_import
from persei import *

from deje.protocol.handler import ProtocolHandler
from deje.action import Action

class PaxosHandler(ProtocolHandler):
    '''
    Handles the serialization of actions.

    deje-paxos-*
    '''

    def start_action(self, doc, callback, action):
        '''
        Propose an action. Callback is called with boolean success.
        '''
        qid = self.toplevel._query(callback)
        content = {
            'qid': qid,
            'action': action.serialize(),
        }
        self.owner.transmit(
            doc,
            'deje-paxos-accept',
            content,
            participants = True,
            subscribers  = False
        )

    def send_accepted(self, doc, action, signatures = None):
        '''
        Send a deje-paxos-accepted for every valid signature
        '''
        quorum = doc.get_quorum(action)
        signers = signatures or quorum.valid_signatures
        for signer in signers:
            self.owner.transmit(
                doc,
                "deje-paxos-accepted",
                {
                    'signer' : signer,
                    'content' : quorum.content,
                    'signature': quorum.transmittable_sig(signer),
                },
                [action.author.key],
                participants = True # includes all signers
            )

    def send_complete(self, doc, action):
        '''
        Send a deje-paxos-complete with all valid signatures
        '''
        quorum = doc.get_quorum(action)
        doc.owner.transmit(
            doc,
            "deje-paxos-complete",
            {
                'signatures' : quorum.sigs_dict(),
                'content' : quorum.content,
            },
            [],
            participants = True # includes all signers
        )
        doc.owner.reply(
            doc,
            'deje-action-completion',
            {
                'content': quorum.content,
                'version': doc.version,
            },
            action.author.key
        )

    def check_quorum(self, doc, action):
        '''
        Check if a quorum is completed-but-not-sent.
        '''
        quorum = doc._qs.get_quorum(action)
        if quorum.ready(doc):
            quorum.enact(doc)
            self.send_complete(doc, action)

    def _on_accept(self, msg, content, ctype, doc):
        action = Action(
            content['action'],
            self.owner.identities
        ).specific()
        quorum = doc._qs.get_quorum(action)
        if action.valid(doc):
            # TODO: Error message for validation failures
            quorum.sign(self.owner.identity)
            self.send_accepted(doc, action)
            self.check_quorum(doc, action)

    def _on_accepted(self, msg, content, ctype, doc):
        sender = self.owner.identities.find_by_location(content['signer'])
        action = Action(content['content'], self.owner.identities).specific()
        content_hash = String(action.hash())
        quorum = doc._qs.get_quorum(action)

        sig = RawData(content['signature'])
        quorum.sign(sender, sig)
        self.check_quorum(doc, action)

    def _on_complete(self, msg, content, ctype, doc):
        action = Action(content['content'], self.owner.identities).specific()
        content_hash = String(action.hash())
        quorum = doc._qs.get_quorum(action)
        for signer in content['signatures']:
            sender = self.owner.identities.find_by_location(signer)
            sig = RawData(content['signatures'][signer])
            quorum.sign(sender, sig)
        self.check_quorum(doc, action)
