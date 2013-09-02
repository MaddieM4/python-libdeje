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

from ejtp.util.compat    import unittest

from deje.event          import Event
from deje.handlers.lua   import handler_document
from deje.tests.identity import identity
from deje.owner          import Owner
from deje.quorum         import Quorum
from deje.quorumspace    import QuorumSpace, QSDoubleSigning

class TestQuorumSpace(unittest.TestCase):

    def setUp(self):
        self.doc = handler_document("tag_team")
        self.mitzi = identity('mitzi')
        self.atlas = identity('atlas')
        self.ev1 = Event({"hello":"world"}, self.mitzi)
        self.ev2 = Event({"turtle":"food"}, self.mitzi)
        self.qs  = self.doc._qs
        self.owner = Owner(self.mitzi, make_jack=False)
        self.owner.own_document(self.doc)
        self.owner.identities.update_ident(self.atlas)

    def test_initial_state(self):
        self.assertEqual(
            sorted(self.ev1.quorum.participants, key = lambda x: x.key),
            [self.atlas, self.mitzi]
        )
        self.assertTrue(self.qs.is_free(self.mitzi))
        self.assertTrue(self.qs.is_free(self.atlas))
        self.assertTrue(self.ev1.quorum.competing)

    def test_double_sign(self):
        # TODO: Break this apart when I better understand the side
        # effects that this test depends on.

        self.ev1.quorum.sign(self.mitzi)
        self.assertFalse(self.qs.is_free(self.mitzi))
        self.assertTrue(self.qs.is_free(self.atlas))
        self.assertEqual(len(self.qs.by_hash), 2)

        self.assertIsInstance(self.qs.by_hash[self.ev1.hash()], Quorum)
        self.assertIsInstance(self.qs.by_hash[self.ev2.hash()], Quorum)

        self.assertEquals(
            self.qs.by_author,
            {self.mitzi.key: self.ev1.quorum}
        )
        self.assertTrue(self.ev1.quorum.competing)
        self.assertFalse(self.ev1.quorum.done)

        # Not double signing, same person and ev
        self.ev1.quorum.sign(self.mitzi)

        # Double signing, same person but different ev
        self.assertRaises(
            QSDoubleSigning,
            self.ev2.quorum.sign,
            self.mitzi
        )

        self.ev1.quorum.sign(self.atlas)
        self.assertTrue(self.qs.is_free(self.mitzi))
        self.assertTrue(self.qs.is_free(self.atlas))
        self.assertFalse(self.ev1.quorum.competing)
        self.assertTrue(self.ev1.quorum.done)
