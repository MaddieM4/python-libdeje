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

from persei import String

import ejtp.client
from ejtp import identity
from deje import protocol
from deje import errors

class Owner(object):
    '''
    Manages documents, identities, and an EJTP client.
    '''
    def __init__(self, self_ident, router=None, make_jack=True):
        self.identities = identity.IdentityCache()
        self.identities.update_ident(self_ident)
        self.identity = self_ident

        self.documents = {}
        self.protocol  = protocol.Protocol(self)
        self.client = ejtp.client.Client(router, self.identity.location, self.identities, make_jack)
        self.client.rcv_callback = self.on_ejtp

    def own_document(self, document):
        document._owner = self
        self.documents[document.name] = document

    # EJTP callbacks

    def on_ejtp(self, msg, client):
        content = msg.unpack()
        # Rule out basic errors
        if type(content) != dict:
            return self.error(msg, errors.MSG_NOT_DICT)
        if not "type" in content:
            return self.error(msg, errors.MSG_NO_TYPE)

        # Accumulate basic information
        mtype = content['type']
        if "docname" in content and content['docname'] in self.documents:
            doc = self.documents[content['docname']]
        else:
            doc = None

        self.protocol.call(msg, content, mtype, doc)

    # Network utility functions

    def transmit(self, document, mtype, properties, targets = [], participants = False, subscribers = True):
        targets = set(targets)
        if participants:
            targets.update(ident.key for ident in document.get_participants())
        if subscribers:
            targets.update(document.subscribers)

        message = { 'type':mtype, 'docname':document.name }
        message.update(properties)
        for target in targets:
            if hasattr(target, 'location'):
                address = target.location
            else:
                try:
                    address = self.identities.find_by_location(target).location
                except KeyError:
                    print("No known address for %r, skipping" % target)
                    break
            if address != self.identity.location:
                self.client.write_json(address, message)
        return targets

    def reply(self, document, mtype, properties, target):
        return self.transmit(document, mtype, properties, [target], subscribers=False)

    def lock_action(self, document, content, actiontype = None):
        self.transmit(document, 'deje-lock-acquire', {'content':content}, participants = True, subscribers=False)

    # Network actions

    def get_version(self, document, callback):
        def wrapped(sender, **kwargs):
            callback(kwargs['version'])
            document.signals['recv-version'].disconnect(wrapped)
        document.signals['recv-version'].connect(wrapped)

        return self.transmit(
            document,
            'deje-get-version',
            {},
            participants = True,
            subscribers = False
        )

    def get_block(self, document, version, callback):
        version = String(version)
        def wrapped(sender, **kwargs):
            if String(kwargs['version']) == version:
                callback(kwargs['block'])
                document.signals['recv-block'].disconnect(wrapped)
        document.signals['recv-block'].connect(wrapped)

        return self.transmit(
            document,
            'deje-get-block',
            {'version':version},
            participants = True,
            subscribers = False
        )

    def get_snapshot(self, document, version, callback):
        version = String(version)
        def wrapped(sender, **kwargs):
            if String(kwargs['version']) == version:
                callback(kwargs['snapshot'])
                document.signals['recv-snapshot'].disconnect(wrapped)
        document.signals['recv-snapshot'].connect(wrapped)

        self.transmit(
            document,
            'deje-get-snapshot',
            {'version':version},
            participants = True,
            subscribers = False
        )

    def error(self, msg, attributes, data=None):
        '''
        Shortcut syntax for replying with error information. Not the same
        functional signature as self.protocol.error!
        '''
        recipient = msg.receiver
        code = attributes['code']
        explanation = attributes['explanation']
        if '%' in explanation:
            explanation = explanation % data

        self.protocol.error([recipient], code, explanation, data)
