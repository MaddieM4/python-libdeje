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

from ejtp.util.compat    import unittest
from deje.handlers       import handler_resource
from deje.tests.identity import identity

from deje.historystate   import HistoryState
from deje.resource       import Resource
from deje.event          import Event

class TestHistoryState(unittest.TestCase):

    def setUp(self):
        self.resource = Resource()

    def test_init(self):
        hs = HistoryState()
        self.assertEqual(hs.hash, None)
        self.assertEqual(hs.resources, {})

    def test_init_with_hash(self):
        hs = HistoryState("example")
        self.assertEqual(hs.hash, "example")
        self.assertEqual(hs.resources, {})

    def test_init_with_resources(self):
        hs = HistoryState(resources=[self.resource])
        self.assertEqual(hs.hash, None)
        self.assertEqual(hs.resources, {'/':self.resource})

    def test_init_with_both(self):
        hs = HistoryState("example", [self.resource])
        self.assertEqual(hs.hash, "example")
        self.assertEqual(hs.resources, {'/':self.resource})

    def test_add_resource(self):
        hs = HistoryState()
        hs.add_resource(self.resource)
        self.assertEqual(hs.resources, {'/':self.resource})

    def test_apply(self):
        res = handler_resource("tag_team")
        hs = HistoryState("example", [res])
        ev = Event(
            {
                'path' : '/handler.lua',
                'property' : 'comment',
                'value' : 'An arbitrary comment',
            },
            identity("mitzi"),
            None
        )
        hs.apply(ev)
        self.assertEqual(res.comment, 'An arbitrary comment')
        self.assertEqual(hs.hash, ev.hash())

    def test_clone(self):
        hs1 = HistoryState("example", [self.resource], "/stanley_gibbons.lua")
        hs2 = hs1.clone()

        # Each resource compared by ref, not value. Use serialization for that.
        self.assertNotEqual(hs1.resources, hs2.resources)
        self.assertEqual(hs1.serialize(), hs2.serialize())

    def test_serialize_resources(self):
        hs = HistoryState("example", [self.resource])
        self.assertEqual(hs.serialize_resources(), {
            '/' : {
                'comment': '',
                'content': '',
                'path': '/',
                'type': 'application/x-octet-stream',
            }
        })

    def test_serialize(self):
        hs = HistoryState("example", [self.resource])
        self.assertEqual(hs.serialize(), {
            "hash" : "example",
            "resources" : hs.serialize_resources(),
            "handler" : "/handler.lua",
        })

    def test_deserialize(self):
        hs1 = HistoryState("example", [self.resource], "/stanley_gibbons.lua")
        hs2 = HistoryState()

        hs2.deserialize(hs1.serialize())

        # Test for value equality
        self.assertNotEqual(hs1.resources, hs2.resources)
        self.assertEqual(hs1.serialize(), hs2.serialize())

    def test_handler(self):
        res = handler_resource("echo_chamber")
        hs = HistoryState("example", [res])
        self.assertEqual(hs.handler, res)

    def test_create_interpreter(self):
        res = handler_resource("tag_team")
        hs = HistoryState("example", [res])
        interp = hs.create_interpreter()
        self.assertEqual(interp.can_read(identity('mitzi')), True)
        self.assertEqual(interp.can_write(identity('victor')), False)

        # Should not be the same/cached
        self.assertNotEqual(interp, hs.create_interpreter())

    def test_interpreter(self):
        res = handler_resource("tag_team")
        hs = HistoryState("example", [res])
        interp = hs.interpreter
        self.assertEqual(interp.can_read(identity('mitzi')), True)
        self.assertEqual(interp.can_write(identity('victor')), False)

        # Should be the same/cached
        self.assertEqual(interp, hs.interpreter)

        # Should not be the same/cached, after hash change
        hs.hash = "some other hash"
        self.assertNotEqual(interp, hs.interpreter)
