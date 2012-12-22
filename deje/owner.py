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
import read
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

        >>> vdoc.version
        0
        >>> vdoc.can_read()
        True
        >>> # One error is normal, due to transmission patterns
        >>> rr = vdoc.subscribe()
        Unknown checkpoint data, dropping
        >>> mdoc.competing
        []
        >>> adoc.competing
        []
        >>> rr #doctest: +ELLIPSIS
        <deje.read.ReadRequest object at ...>
        >>> mdoc.subscribers #doctest: +ELLIPSIS
        set([<deje.identity.Identity object at ...>])
        >>> adoc.subscribers #doctest: +ELLIPSIS
        set([<deje.identity.Identity object at ...>])
        '''
        content = msg.jsoncontent
        # Rule out basic errors
        if type(content) != dict:
            print "Recieved non-{} message, dropping"
            return
        if not "type" in content:
            print "Recieved message with no type, dropping"
            return

        # Accumulate basic information
        mtype = content['type']
        if "docname" in content and content['docname'] in self.documents:
            doc = self.documents[content['docname']]
        else:
            doc = None
        if mtype == "deje-lock-acquire":
            self._on_deje_lock_acquire(msg, content, mtype, doc)
        elif mtype == "deje-lock-acquired":
            self._on_deje_lock_acquired(msg, content, mtype, doc)
        elif mtype == "deje-lock-complete":
            self._on_deje_lock_complete(msg, content, mtype, doc)
        else:
            print "Recieved message with unknown type (%r)" % mtype

    def _on_deje_lock_acquire(self, msg, content, ctype, doc):
        lcontent = content['content']
        ltype = lcontent['type']
        if ltype == "deje-checkpoint":
            cp_content = lcontent['checkpoint']
            cp_version = lcontent['version']
            cp_author  = lcontent['author']

            cp = checkpoint.Checkpoint(doc, cp_content, cp_version, cp_author)
            if doc.can_write(cp_author) and cp.test():
                cp.quorum.sign(self.identity)
                cp.quorum.transmit([self.identity.name])
        if ltype == "deje-subscribe":
            rr_subname = lcontent['subscriber']
            subscriber = self.identities.find_by_name(rr_subname)
            rr = read.ReadRequest(doc, subscriber)
            if doc.can_read(subscriber):
                rr.sign(self.identity)
                rr.update()

    def _on_deje_lock_acquired(self, msg, content, ctype, doc):
        sender = self.identities.find_by_name(content['signer'])
        try:
            cp = doc._qs.by_hash[content['content-hash']].parent
        except KeyError:
            print "Unknown checkpoint data, dropping"
            return
        sig = content['signature'].encode('raw_unicode_escape')
        cp.quorum.sign(sender, sig)
        cp.update()

    def _on_deje_lock_complete(self, msg, content, ctype, doc):
        try:
            quorum = doc._qs.by_hash[content['content-hash']]
        except KeyError:
            print "Unknown checkpoint data for complete, dropping (%r)" % content['content-hash']
            return
        for signer in content['signatures']:
            sender = self.identities.find_by_name(signer)
            sig = content['signatures'][signer].encode('raw_unicode_escape')
            quorum.sign(sender, sig)
            quorum.parent.update()

    def on_lock_succeed(self, document, content):
        pass

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

    def lock_action(self, document, content, actiontype = None):
        self.transmit(document, 'deje-lock-acquire', {'content':content}, participants = True, subscribers=False)

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

    def error(self, recipients, code, explanation="", data={}):
        for r in recipients:
            self.client.write_json(r, {
                'type':'deje-error',
                'code':int(code),
                'explanation':str(explanation),
                'data':data,
            })
