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
from deje import errors

from deje.protocol.handler  import ProtocolHandler
from deje.protocol.retrieve import RetrieveHandler
from deje.protocol.locking  import LockingHandler

class DejeHandler(ProtocolHandler):
    def __init__(self, parent):
        ProtocolHandler.__init__(self, parent)
        self._on_retrieve = RetrieveHandler(self)
        self._on_lock     = LockingHandler(self)

    def _on_error(self, msg, content, ctype, doc):
        sender = msg.sender
        try:
            sender = self.owner.identities.find_by_location(sender).name
        except KeyError:
            pass # No saved information on this ident
        print("Error from %r, code %d: %r" % (sender, content['code'], content['explanation']))

class ProtocolToplevel(object):
    def __init__(self, owner):
        self.owner = owner
        self._on_deje = DejeHandler(self)

    def call(self, msg, content, ctype, doc):
        '''
        Find and call protocol function
        '''
        chain = ctype.split('-')
        handler = self
        for item in chain:
            item = "_on_" + item
            if hasattr(handler, item):
                handler = getattr(handler, item)
            else:
                return self.owner.error(msg, errors.MSG_UNKNOWN_TYPE, ctype)

        if not callable(handler):
            return self.owner.error(msg, errors.MSG_UNKNOWN_TYPE, ctype)

        return handler(msg, content, ctype, doc)

    # Transport shortcuts

    def error(self, recipients, code, explanation="", data={}):
        for r in recipients:
            self.owner.client.write_json(r, {
                'type':'deje-error',
                'code':int(code),
                'explanation':str(explanation),
                'data':data,
            })
