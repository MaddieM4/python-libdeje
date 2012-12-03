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
        >>> from deje import testing
        >>> badident = testing.identity()
        >>> badident.location = None
        >>> Owner(badident, None, False)
        Traceback (most recent call last):
        AttributeError: Identity location not set

        Do setup for testing a good owner.
        >>> owner = testing.owner()
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

    def own_document(self, document):
        document._owner = self

    # Checkpoint callbacks

    def attempt_checkpoint(self, document, checkpoint):
        self.update_checkpoint(document, checkpoint)
        # TODO: Send stuff over the network

    def update_checkpoint(self, document, checkpoint):
        if checkpoint.has_quorum(document):
            self.complete_checkpoint(document, checkpoint)

    def complete_checkpoint(self, document, checkpoint):
        checkpoint.enact(document)
        # TODO: Send stuff over the network
