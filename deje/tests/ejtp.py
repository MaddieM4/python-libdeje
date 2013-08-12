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

from deje.tests.stream   import StreamTest
from ejtp.router         import Router
from deje.owner          import Owner
from deje.handlers.lua   import handler_document
from deje.tests.identity import identity

class TestEJTP(StreamTest):

    def setUp(self):
        StreamTest.setUp(self)

        self.router = Router()
        self.mitzi  = Owner(identity("mitzi"),  self.router)
        self.atlas  = Owner(identity("atlas"),  self.router)
        self.victor = Owner(identity("victor"), self.router)
        self.mitzi.identities.sync(
            self.atlas.identities,
            self.victor.identities,
        )

        # Document that mitzi and atlas are part of, but victor is not.
        # Separate identical starting points for all of them.
        self.mdoc = handler_document("tag_team")
        self.adoc = handler_document("tag_team")
        self.vdoc = handler_document("tag_team")
        self.mitzi.own_document(self.mdoc)
        self.atlas.own_document(self.adoc)
        self.victor.own_document(self.vdoc)
