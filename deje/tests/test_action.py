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

from ejtp.util.compat    import unittest
from ejtp.identity       import Identity, IdentityCache
from deje.tests.identity import identity

from deje.action         import Action
from deje.read           import ReadRequest

class TestRead(unittest.TestCase):
    def setUp(self):
        self.mitzi = identity('mitzi')
        self.cache = IdentityCache()
        self.rr    = ReadRequest(self.mitzi)

        self.cache.update_ident(self.mitzi)

    def test_serialize_eq_self(self):
        # No change between runs
        self.assertEqual(
            self.rr.serialize(),
            self.rr.serialize()
        )

    def test_serialize_keys(self):
        serialized = self.rr.serialize()
        self.assertEqual(
            sorted(serialized.keys()),
            ['author', 'type', 'unique']
        )

    def test_serialize_cycle(self):
        serialized = self.rr.serialize()
        rr2 = Action(serialized, self.cache).specific()
        self.assertEqual(serialized, rr2.serialize())
