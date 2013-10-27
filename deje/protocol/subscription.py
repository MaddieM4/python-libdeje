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
from deje.subscription     import Subscription
from deje                  import errors

class SubscriptionHandler(ProtocolHandler):

    def __init__(self, parent):
        ProtocolHandler.__init__(self, parent)
        subscriptions   = {}

        self._on_add    = SubAddHandler(self)
        self._on_remove = SubRemoveHandler(self)
        self._on_list   = SubListHandler(self)

    def subscribe(self, sub):
        self.subscriptions[sub.hash()] = sub

    def unsubscribe(self, hash):
        if hash in self.subscriptions:
            del self.subscriptions[hash]

class SubAddHandler(ProtocolHandler):
    '''
    Create a new Subscription, pointing to yourself, from the remote end.
    '''

    def _on_query(self, msg, content, ctype, doc):
        qid    = int(content['qid'])
        source = msg.receiver
        target = msg.sender
        if 'expiration' in content:
            expiration = content['expiration']
        if not doc.can_read(target):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)

        sub = Subscription(source, target, doc.name, expiration)
        self.parent.subscribe(sub)
        self.owner.reply(
            doc,
            'deje-sub-add-response',
            {
                'qid': qid,
                'subscription': sub.serialize(),
            },
            target.key
        )

    def _on_response(self, msg, content, ctype, doc):
        qid = int(content['qid'])
        sub = Subscription()
        sub.deserialize(content['subscription'])
        self.parent.subscribe(sub)

class SubRemoveHandler(ProtocolHandler):
    '''
    Remove a remote subscription, referencing it by its hash.

    deje-sub-remove-*
    '''

    def _on_query(self, msg, content, ctype, doc):
        qid  = int(content['qid'])
        subh = content['hash']

        success = subh in self.parent.subscriptions
        self.parent.unsubscribe(subh)
        self.owner.reply(
            doc,
            'deje-sub-remove-response',
            {
                'qid': qid,
                'success': success,
            },
            msg.sender.key
        )

    def _on_response(self, msg, content, ctype, doc):
        qid = int(content['qid'])
        success = content['success']
        # TODO: Use this value in some way

class SubListHandler(ProtocolHandler):
    '''
    List all your subscriptions on a remote source.

    Note that these are across all documents, and therefore don't have a doc
    param, contrary to most message types.

    deje-sub-list-*
    '''

    def _on_query(self, msg, content, ctype, doc):
        qid    = int(content['qid'])
        if 'hashes' in content:
            hashes = content['hashes']
        else:
            hashes = self.parent.subscriptions.keys()

        subs = {}
        for h in hashes:
            subs[h] = self.parent.subscriptions[h]

        self.owner.reply(
            doc,
            'deje-sub-remove-response',
            {
                'qid': qid,
                'subs': subs,
            },
            msg.sender.key
        )

    def _on_response(self, msg, content, ctype, doc):
        qid  = int(content['qid'])
        subs = content['subs']
        # TODO: Use this value in some way
