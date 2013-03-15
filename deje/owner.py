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

import ejtp.client
from ejtp import identity
import protocol
import errors

class Owner(object):
    '''
    Manages documents, identities, and an EJTP client.
    '''
    def __init__(self, self_ident, router=None, make_jack=True):
        '''
        Make sure string idents fail
        >>> from ejtp.router import Router
        >>> anon = Owner("anonymous", Router())
        Traceback (most recent call last):
        AttributeError: 'str' object has no attribute 'location'

        Make sure self_idents with no location fail
        >>> import testing
        >>> badident = testing.identity()
        >>> badident.location = None
        >>> Owner(badident, None, False)
        Traceback (most recent call last):
        TypeError: str_address() takes exactly 1 argument (0 given)

        Do setup for testing a good owner.
        >>> owner = testing.owner()
        >>> owner.identities #doctest: +ELLIPSIS
        <IdentityCache '{\\'["local",null,"mitzi"]\\': <ejtp.identity.core.Identity object at ...>}'>
        >>> doc = testing.document(handler_lua_template="echo_chamber")
        >>> doc.handler #doctest: +ELLIPSIS
        <deje.resource.Resource object at ...>
        >>> owner.own_document(doc)

        '''
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
        '''
        >>> import testing
        >>> mitzi, atlas, victor, mdoc, adoc, vdoc = testing.ejtp_test()

        >>> mitzi.identity.location
        ['local', None, 'mitzi']
        >>> atlas.identity.location
        ['local', None, 'atlas']
        >>> mitzi.client.interface == mitzi.identity.location
        True
        >>> r = mitzi.client.router
        >>> r.client(mitzi.identity.location) == mitzi.client
        True
        >>> atlas.client.interface == atlas.identity.location
        True
        >>> mitzi.client.router == atlas.client.router
        True

        Test raw EJTP connectivity with a malformed message
        >>> atlas.client.write_json(mitzi.identity.location, "Oompa loompa")
        Error from 'mitzi@lackadaisy.com', code 30: u'Recieved non-{} message, dropping'
        '''
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
            targets.update(set(document.get_participants()))
        if subscribers:
            targets.update(document.subscribers)

        message = { 'type':mtype, 'docname':document.name }
        message.update(properties)
        for target in targets:
            # print target, mtype
            if hasattr(target, 'location'):
                address = target.location
            else:
                try:
                    address = self.identities.find_by_name(target).location
                except KeyError:
                    print "No known address for %r, skipping" % target
                    break
            if address != self.identity.location:
                self.client.write_json(address, message)

    def reply(self, document, mtype, properties, target):
        return self.transmit(document, mtype, properties, [target], subscribers=False)

    def lock_action(self, document, content, actiontype = None):
        self.transmit(document, 'deje-lock-acquire', {'content':content}, participants = True, subscribers=False)

    # Network actions

    def get_version(self, document, callback):
        """
        >>> import testing
        >>> mitzi, atlas, victor, mdoc, adoc, vdoc = testing.ejtp_test()
        >>> def on_recv_version(version):
        ...     print "Version is %d" % version
        >>> victor.get_version(vdoc, on_recv_version)
        Version is 0
        >>> mcp = mdoc.checkpoint({ #doctest: +ELLIPSIS
        ...     'path':'/example',
        ...     'property':'content',
        ...     'value':'Mitzi says hi',
        ... })
        >>> victor.get_version(vdoc, on_recv_version)
        Version is 1
        """
        document.set_callback('recv-version', callback)
        self.transmit(document, 'deje-get-version', {}, participants = True, subscribers = False)

    def get_block(self, document, version, callback):
        """
        >>> import json
        >>> import testing
        >>> mitzi, atlas, victor, mdoc, adoc, vdoc = testing.ejtp_test()

        Print in a predictible manner for doctest

        >>> def on_recv_block(block):
        ...     print json.dumps(block, indent=4, sort_keys=True)

        Put in a checkpoint to retrieve

        >>> mcp = mdoc.checkpoint({ #doctest: +ELLIPSIS
        ...     'path':'/example',
        ...     'property':'content',
        ...     'value':'Mitzi says hi',
        ... })

        Retrieve checkpoint

        >>> victor.get_block(vdoc, 0, on_recv_block) #doctest: +ELLIPSIS
        {
            "author": "mitzi@lackadaisy.com", 
            "content": {
                "path": "/example", 
                "property": "content", 
                "value": "Mitzi says hi"
            }, 
            "signatures": {
                "atlas@lackadaisy.com": "...", 
                "mitzi@lackadaisy.com": "..."
            }, 
            "version": 0
        }
        """
        document.set_callback('recv-block-%d' % version, callback)
        self.transmit(document, 'deje-get-block', {'version':version}, participants = True, subscribers = False)

    def get_snapshot(self, document, version, callback):
        """
        >>> import json
        >>> import testing
        >>> mitzi, atlas, victor, mdoc, adoc, vdoc = testing.ejtp_test()
        >>> def on_recv_snapshot(snapshot):
        ...     print json.dumps(snapshot, indent=4, sort_keys=True)

        >>> victor.get_snapshot(vdoc, 0, on_recv_snapshot) #doctest: +ELLIPSIS
        {
            "/handler.lua": {
                "comment": "The primary handler", 
                "content": "\\n        function checkpoint_test(cp, author)...", 
                "path": "/handler.lua", 
                "type": "text/lua"
            }
        }
        """
        document.set_callback('recv-snapshot-%d' % version, callback)
        self.transmit(document, 'deje-get-snapshot', {'version':version}, participants = True, subscribers = False)

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
