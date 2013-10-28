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
        self.subscriptions = {}

        self._on_add    = SubAddHandler(self)
        self._on_remove = SubRemoveHandler(self)
        self._on_list   = SubListHandler(self)

    def subscribe(self, sub):
        self.subscriptions[sub.hash()] = sub

    def unsubscribe(self, hash):
        if hash in self.subscriptions:
            del self.subscriptions[hash]

    def subscribers(self, doc):
        name = doc.name
        return tuple(
            self.identity(s.target) for s in self.subscriptions.values()
            if s.source == self.owner.identity.location
        )

class SubAddHandler(ProtocolHandler):
    '''
    Create a new Subscription, pointing to yourself, from the remote end.
    '''

    def subscribe(self,doc,callback,sources,expiration=None):
        for source in sources:
            qid = self.toplevel._query(callback)
            content = { 'qid': qid }
            if expiration:
                content['expiration'] = expiration
            self.send(
                doc,
                'deje-sub-add-query',
                content,
                source.key
            )

    def _on_query(self, msg, content, ctype, doc):
        qid    = int(content['qid'])
        source = self.identity(msg.receiver)
        target = self.identity(msg.sender)
        if 'expiration' in content:
            expiration = content['expiration']
        else:
            expiration = None
        if not doc.can_read(target):
            return self.owner.error(msg, errors.PERMISSION_CANNOT_READ)

        sub = Subscription(
            source.location,
            target.location,
            doc.name,
            expiration
        )
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
        self.toplevel._on_response(qid, [sub])

class SubRemoveHandler(ProtocolHandler):
    '''
    Remove a remote subscription, referencing it by its hash.

    deje-sub-remove-*
    '''

    def unsubscribe(self, doc, callback, sub):
        qid   = self.toplevel._query(callback)
        subh  = sub.hash()
        ident = self.identity(sub.source)
        self.send(
            doc,
            'deje-sub-remove-query',
            {
                'qid' : qid,
                'hash': subh,
            },
            ident.key
        )

    def _on_query(self, msg, content, ctype, doc):
        qid  = int(content['qid'])
        subh = String(content['hash'])

        success = subh in self.parent.subscriptions
        self.parent.unsubscribe(subh)
        self.send(
            doc,
            'deje-sub-remove-response',
            {
                'qid': qid,
                'success': success,
            },
            self.identity(msg.sender).key
        )

    def _on_response(self, msg, content, ctype, doc):
        qid = int(content['qid'])
        success = content['success']
        self.toplevel._on_response(qid, [success])

class SubListHandler(ProtocolHandler):
    '''
    List all your subscriptions on a remote source.

    Note that these are across all documents, and therefore don't have a doc
    param, contrary to most message types.

    deje-sub-list-*
    '''

    def get_subs(self, source, callback, hashes=[]):
        qid     = self.toplevel._query(callback)
        ident   = self.identity(source)
        content = {
            'type' : 'deje-sub-list-query',
            'qid'  : qid,
        }

        if hashes:
            content['hashes'] = hashes

        self.write_json(ident.location, content)

    def _on_query(self, msg, content, ctype, doc):
        qid = int(content['qid'])
        if 'hashes' in content:
            hashes = content['hashes']
        else:
            hashes = [
                s.hash() for s in self.parent.subscriptions.values()
                if s.source == self.owner.identity.location
                    and s.target == msg.sender
            ]

        subs = {}
        for h in hashes:
            subs[h] = self.parent.subscriptions[h].serialize()

        content = {
            'type': 'deje-sub-list-response',
            'qid' : qid,
            'subs': subs,
        }
        self.write_json(msg.sender, content)

    def _on_response(self, msg, content, ctype, doc):
        qid  = int(content['qid'])
        subs = content['subs']

        # Deserialize
        for h in subs:
            sub_obj = Subscription()
            sub_obj.deserialize(subs[h])
            subs[h] = sub_obj

        self.toplevel._on_response(qid, [subs])
