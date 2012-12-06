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
        self.client.rcv_message = self.on_ejtp

    def own_document(self, document):
        document._owner = self

    # EJTP callbacks

    def on_ejtp(self, msg, client):
        '''
        >>> import testing
        >>> from ejtp.router import Router
        >>> r = Router()
        >>> mitzi  = Owner(testing.identity("mitzi"),  r)
        >>> atlas  = Owner(testing.identity("atlas"),  r)
        >>> victor = Owner(testing.identity("victor"), r)
        >>> anon   = Owner("anonymous", r)
        Traceback (most recent call last):
        AttributeError: 'str' object has no attribute 'location'
        
        Document that mitzi and atlas are part of, but victor is not.
        Separate identical starting points for all of them.
        >>> mdoc = testing.document(handler_lua_template="tag_team")
        >>> adoc = testing.document(handler_lua_template="tag_team")
        >>> mitzi.own_document(mdoc)
        >>> atlas.own_document(adoc)

        >>> mdoc.checkpoint({
        ...     'path':'/example',
        ...     'content':'Mitzi says hi',
        ... })
        '''
        print msg

    def on_lock_succeed(self, document, content):
        pass

    # Network utility functions

    def transmit(self, document, mtype, **kwargs):
        participants = document.get_participants()
        message = { 'type':mtype, 'docname':document.name }
        message.update(kwargs)
        for p in participants:
            address = self.identities.find_by_name(p).location
            self.client.write_json(address, message)

    def lock_action(self, document, content):
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

    # Checkpoint callbacks

    def attempt_checkpoint(self, document, checkpoint):
        checkpoint.transmit()
        self.update_checkpoint(document, checkpoint)

    def update_checkpoint(self, document, checkpoint):
        if checkpoint.quorum.done:
            self.complete_checkpoint(document, checkpoint)

    def complete_checkpoint(self, document, checkpoint):
        checkpoint.enact(document)
