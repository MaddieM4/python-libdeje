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
from ejtp.tests.test_scripts import IOMock

from deje.event import Event
from deje.quorum import Quorum
from deje.handlers     import handler_document
from deje.tests.identity import identity
from deje.owner import Owner

class TestEvent(unittest.TestCase):

    def setUp(self):
        self.doc = handler_document('echo_chamber')
        self.ident = identity()
        self.ev  = Event({'x':'y'}, self.ident, 'stormageddon')
        self.quorum = Quorum(self.ev, self.doc._qs)
        self.owner = Owner(self.ident, make_jack=False)
        self.owner.own_document(self.doc)
        self.io = IOMock()

    def test_init(self):
        self.assertEqual(self.ev.version, 'stormageddon')
        self.quorum.sign(self.ident)
        self.assertEqual(
            self.quorum.participants,
            [self.ident]
        )
        self.assertTrue(self.quorum.sig_valid(self.ident.key))
        self.assertRaises(
            TypeError,
            self.quorum.sign,
            "some string"
        )
        self.assertFalse(self.quorum.sig_valid("some string"))

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
            String('ce9950bb5a8db63712ae1ecfe9269e22289673ec')
        )

    def test_serialize(self):
        self.assertEqual(
            self.ev.serialize(),
            {
                'type': 'event',
                'author': ['local', None, 'mitzi'],
                'content': {'x':'y'},
                'version': 'stormageddon',
            }
        )

    def test_enact(self):
        self.assertEqual(self.ev.is_done(self.doc), False)
        with self.io:
            self.ev.enact(self.quorum, self.doc)
        self.assertEqual(self.ev.is_done(self.doc), True)
