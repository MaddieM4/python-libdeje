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
from persei import String

from ejtp.util.compat import unittest
from ejtp.identity.core import Identity

from deje.event import Event
from deje.quorum import Quorum
from deje.handlers.lua import handler_document
from deje.tests.identity import identity
from deje.owner import Owner

class TestEvent(unittest.TestCase):

    def setUp(self):
        self.doc = handler_document('echo_chamber')
        self.ident = identity()
        self.ev  = Event({'x':'y'}, self.ident, 'stormageddon')
        self.ev.quorum = Quorum(self.ev, self.doc._qs)
        self.owner = Owner(self.ident, make_jack=False)
        self.owner.own_document(self.doc)

    def test_init(self):
        self.assertEqual(self.ev.version, 'stormageddon')
        self.ev.quorum.sign(self.ident)
        self.assertEqual(
            self.ev.quorum.participants,
            [self.ident]
        )
        self.assertTrue(self.ev.quorum.sig_valid(self.ident.key))
        self.assertRaises(
            TypeError,
            self.ev.quorum.sign,
            "some string"
        )
        self.assertFalse(self.ev.quorum.sig_valid("some string"))

    def test_authorname(self):
        # Override ev for this test
        self.ev = Event(None, self.owner.identity)

        self.assertTrue(
            isinstance(self.ev.author, Identity)
        )
        self.assertEqual(
            self.ev.authorname,
            'mitzi@lackadaisy.com'
        )
        self.assertEqual(
            self.doc.identity.name,
            'mitzi@lackadaisy.com'
        )

    def test_hash(self):
        self.assertEqual(
            self.ev.hash(),
            String('92395fb63e777d342d75915ad25dde1172e20f7c')
        )

    def test_hashcontent(self):
        self.assertEqual(
            self.ev.hashcontent,
            [{'x': 'y'}, 'stormageddon', 'mitzi@lackadaisy.com']
        )
