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
import identity
import checkpoint
import document

class Owner(object):
    '''
    Manages documents, identities, and an EJTP client.
    '''
    def __init__(self, self_ident, router=None, make_jack=True):
        '''

        Make sure self_idents with no location fail
        >>> import testing
        >>> badident = testing.identity()
        >>> badident.location = None
        >>> Owner(badident, None, False)
        Traceback (most recent call last):
        AttributeError: Identity location not set

        Do setup for testing a good owner.
        >>> owner = testing.owner()
        >>> owner.identities #doctest: +ELLIPSIS
        <EncryptorCache '{\\'["local",null,"mitzi"]\\': <deje.identity.Identity object at ...>}'>
        >>> doc = testing.document(handler_lua_template="echo_chamber")
        >>> doc.handler #doctest: +ELLIPSIS
        <deje.resource.Resource object at ...>
        >>> owner.own_document(doc)

        '''
        self.identities = identity.EncryptorCache()
        self.identities.update_ident(self_ident)
        self.identity = self_ident

        self.documents  = {}
        self.client = ejtp.client.Client(router, self.identity.location, self.identities, make_jack)
        self.client.rcv_callback = self.on_ejtp

    def own_document(self, document):
        document._owner = self
        self.documents[document.name] = document

    # EJTP callbacks

    def on_ejtp(self, msg, client):
        '''
        >>> import testing
        >>> import identity
        >>> from ejtp.router import Router
        >>> r = Router()
        >>> mitzi  = Owner(testing.identity("mitzi"),  r)
        >>> atlas  = Owner(testing.identity("atlas"),  r)
        >>> victor = Owner(testing.identity("victor"), r)
        >>> identity.sync_caches(
        ...     mitzi.identities,
        ...     atlas.identities,
        ...     victor.identities,
        ... )
        >>> anon   = Owner("anonymous", r)
        Traceback (most recent call last):
        AttributeError: 'str' object has no attribute 'location'
        
        Document that mitzi and atlas are part of, but victor is not.
        Separate identical starting points for all of them.
        >>> mdoc = testing.document(handler_lua_template="tag_team")
        >>> adoc = testing.document(handler_lua_template="tag_team")
        >>> vdoc = testing.document(handler_lua_template="tag_team")
        >>> mitzi.own_document(mdoc)
        >>> atlas.own_document(adoc)
        >>> victor.own_document(vdoc)

        Test raw EJTP connectivity with a malformed message
        >>> mitzi.identity.location
        ['local', None, 'mitzi']
        >>> atlas.identity.location
        ['local', None, 'atlas']
        >>> mitzi.client.interface == mitzi.identity.location
        True
        >>> r.client(mitzi.identity.location) == mitzi.client
        True
        >>> atlas.client.interface == atlas.identity.location
        True
        >>> mitzi.client.router == atlas.client.router
        True
        >>> atlas.client.write_json(mitzi.identity.location, "Oompa loompa")
        Recieved non-{} message, dropping

        Test a write
        >>> mcp = mdoc.checkpoint({ #doctest: +ELLIPSIS
        ...     'path':'/example',
        ...     'property':'content',
        ...     'value':'Mitzi says hi',
        ... })
        >>> mcp.quorum.completion
        2
        >>> mdoc.competing
        []
        >>> mdoc.get_resource("/example").content
        u'Mitzi says hi'
        >>> adoc.get_resource("/example").content
        u'Mitzi says hi'

        Test a read

        TODO:
            * Reengineer ReadRequest/Quorum/WhateverClass for ghost-colliding reads
            * Add Document.subscribe function
        >>> vdoc.version
        0
        >>> vdoc.can_read()
        True
        >>> rr = vdoc.subscribe()
        >>> rr #doctest: +ELLIPSIS
        <deje.read.ReadRequest object at ...>
        '''
        content = msg.jsoncontent
        if type(content) != dict:
            print "Recieved non-{} message, dropping"
            return
        if not "type" in content:
            print "Recieved message with no type, dropping"
            return
        mtype = content['type']
        if mtype == "deje-lock-acquire":
            lcontent = content['content']
            ltype = lcontent['type']
            if ltype == "deje-checkpoint":
                doc = self.documents[content['docname']]
                cp_content = lcontent['checkpoint']
                cp_version = lcontent['version']
                cp_author  = lcontent['author']

                cp = checkpoint.Checkpoint(doc, cp_content, cp_version, cp_author)
                if cp.test():
                    cp.quorum.sign(self.identity)
                    cp.quorum.transmit([self.identity.name])
        elif mtype == "deje-lock-acquired":
            sender = self.identities.find_by_name(content['signer'])
            doc = self.documents[content['docname']]
            try:
                cp = doc._qs.by_hash[content['content-hash']].parent
            except KeyError:
                print "Unknown checkpoint data, dropping"
            sig = content['signature'].encode('raw_unicode_escape')
            cp.quorum.sign(sender, sig)
            cp.update()

    def on_lock_succeed(self, document, content):
        pass

    # Network utility functions

    def transmit(self, document, mtype, **kwargs):
        participants = document.get_participants()
        message = { 'type':mtype, 'docname':document.name }
        message.update(kwargs)
        for p in participants:
            try:
                address = self.identities.find_by_name(p).location
            except KeyError:
                print "No known address for %r, skipping" % p
                break
            if address != self.identity.location:
                self.client.write_json(address, message)

    def lock_action(self, document, content, actiontype = None):
        self.transmit(document, 'deje-lock-acquire', content=content)

    # Network actions

    def get_version(self, document, callback):
        self.lock_action(document, {
            'type':'deje-get-version',
            'reply-to': self.identity,
        })

    def get_block(self, document, callback):
        pass

    def get_snapshot(self, document, callback):
        pass

    def error(self, document, recipients, code, explanation="", data={}):
        for r in recipients:
            self.client.write_json(r, {
                'type':'deje-error',
                'code':int(code),
                'explanation':str(explanation),
                'data':data,
            })
