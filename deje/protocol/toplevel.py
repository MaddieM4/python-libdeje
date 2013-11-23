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
from random import randint

from deje import errors
from deje.protocol.deje import DejeHandler

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
                raise AttributeError("No proto handling for ctype", ctype)
        return handler

    def call(self, message):
        '''
        Find and call protocol function
        '''
        mtype = message.type
        try:
            handler = self.find(mtype)
        except AttributeError:
            handler = None # Catch in next failure handler

        if not callable(handler):
            return self.owner.error(message.msg, errors.MSG_UNKNOWN_TYPE, mtype)

        return handler(message)

    def _register(self, qid, callback):
        self.callbacks[qid] = callback

    def _query(self, callback):
        qid = randint(0, 2**32)
        self._register(qid, callback)
        return qid

    def _on_response(self, qid, args):
        if qid in self.callbacks:
            callback = self.callbacks.pop(qid)
            callback(*args)

    # Accessors

    def subscribers(self, doc):
        return self.find('deje-sub').subscribers(doc)

    @property
    def paxos(self):
        return self.find('deje-paxos')

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

    def error(self, recipients, code, msg="", data={}, qid=0):
        for r in recipients:
            self.owner.client.write_json(r, {
                'type':'deje-error',
                'qid' :int(code),
                'code':int(code),
                'msg' :str(msg),
                'data':data,
            })
