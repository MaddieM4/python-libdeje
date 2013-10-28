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

from __future__ import print_function
from random import randint

from deje import errors

from deje.protocol.handler      import ProtocolHandler
from deje.protocol.retrieve     import RetrieveHandler
from deje.protocol.locking      import LockingHandler
from deje.protocol.subscription import SubscriptionHandler

class DejeHandler(ProtocolHandler):
    def __init__(self, parent):
        ProtocolHandler.__init__(self, parent)
        self._on_retrieve = RetrieveHandler(self)
        self._on_lock     = LockingHandler(self)
        self._on_sub      = SubscriptionHandler(self)

    def _on_error(self, msg, content, ctype, doc):
        sender = msg.sender
        try:
            sender = self.owner.identities.find_by_location(sender).name
        except KeyError:
            pass # No saved information on this ident
        print("Error from %r, code %d: %r" % (sender, content['code'], content['explanation']))

class ProtocolToplevel(object):
    def __init__(self, owner):
        self.owner     = owner
        self.callbacks = {}
        self._on_deje  = DejeHandler(self)

    @property
    def toplevel(self):
        return self

    def find(self, ctype):
        '''
        Get object for a given message type.
        '''
        chain = ctype.split('-')
        handler = self
        for item in chain:
            item = "_on_" + item
            if hasattr(handler, item):
                handler = getattr(handler, item)
            else:
                return self.owner.error(msg, errors.MSG_UNKNOWN_TYPE, ctype)
        return handler

    def call(self, msg, content, ctype, doc):
        '''
        Find and call protocol function
        '''
        handler = self.find(ctype)

        if not callable(handler):
            return self.owner.error(msg, errors.MSG_UNKNOWN_TYPE, ctype)

        return handler(msg, content, ctype, doc)

    def _query(self, callback):
        qid = randint(0, 2**32)
        self.callbacks[qid] = callback
        return qid

    def _on_response(self, qid, args):
        callback = self.callbacks.pop(qid)
        callback(*args)

    # Accessors

    def subscribers(self, doc):
        return self.find('deje-sub').subscribers(doc)

    # Transport shortcuts

    def subscribe(self, doc, callback, sources):
        '''
        Callback will be called for each source, with
        Subscription object as argument.
        '''
        handler = self.find('deje-sub-add')
        handler.subscribe(doc, callback, sources)

    def unsubscribe(self, doc, callback, sub):
        '''
        Callback will be called with args (success).
        '''
        handler = self.find('deje-sub-remove')
        handler.unsubscribe(doc, callback, sub)

    def get_subs(self, source, callback):
        '''
        Callback will be called with args (subs), where subs is
        a dict of { hash : Subscription object }.
        '''
        handler = self.find('deje-sub-list')
        handler.get_subs(source, callback)

    def error(self, recipients, code, explanation="", data={}):
        for r in recipients:
            self.owner.client.write_json(r, {
                'type':'deje-error',
                'code':int(code),
                'explanation':str(explanation),
                'data':data,
            })
