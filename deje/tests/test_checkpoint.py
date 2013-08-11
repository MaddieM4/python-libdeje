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

from persei import String

from ejtp.util.compat import unittest
from ejtp.identity.core import Identity

from deje.checkpoint import Checkpoint
from deje.handlers.lua import handler_document
from deje.tests.identity import identity
from deje.owner import Owner

class TestCheckpoint(unittest.TestCase):

    def setUp(self):
        self.doc = handler_document('echo_chamber')
        self.cp  = Checkpoint(self.doc, {'x':'y'}, 0, 'mick-and-bandit')
        self.ident = identity()
        self.owner = Owner(self.ident, make_jack=False)
        self.owner.own_document(self.doc)

    def test_init(self):
        self.assertEqual(self.cp.version, 0)
        self.cp.quorum.sign(self.ident)
        self.assertEqual(
            self.cp.quorum.participants,
            ['mitzi@lackadaisy.com']
        )
        self.assertTrue(self.cp.quorum.sig_valid(self.ident.name))
        self.assertRaises(
            TypeError,
            self.cp.quorum.sign,
            "some string"
        )
        self.assertFalse(self.cp.quorum.sig_valid("some string"))

    def test_authorname(self):
        # Override cp for this test
        self.cp = Checkpoint(self.doc, None, author=self.owner.identity)

        self.assertTrue(
            isinstance(self.cp.author, Identity)
        )
        self.assertEqual(
            self.cp.authorname,
            'mitzi@lackadaisy.com'
        )
        self.assertEqual(
            self.doc.identity.name,
            'mitzi@lackadaisy.com'
        )

    def test_hash(self):
        self.assertEqual(
            self.cp.hash(),
            String('a6aa316b4b784fda1a38b53730d1a7698c3c1a33')
        )
