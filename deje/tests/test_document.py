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

#from persei import String

from ejtp.util.compat import unittest
from ejtp.router      import Router
from ejtp.identity.core  import Identity

from deje.document import Document, save_to, load_from
from deje.resource import Resource
from deje.owner    import Owner
from deje.handlers.lua   import handler_document
from deje.tests.identity import identity
from deje.read     import ReadRequest

class TestDocumentSimple(unittest.TestCase):

    def setUp(self):
        self.doc = Document("testing")

    def test_serialize(self):
        serial = self.doc.serialize()
        self.assertEqual(
            sorted(serial.keys()),
            ['events', 'original']
        )
        self.assertEqual(serial['original'], {})
        self.assertEqual(serial['events'],   [])

        self.doc.add_resource(
            Resource(path="/example", content="example")
        )
        self.assertEqual(self.doc.serialize()['original'], {})
        self.doc.freeze()
        self.assertEqual(
            self.doc.serialize()['original'],
            {
                "/example": {
                    "comment": "",
                    "content": "example",
                    "path":    "/example",
                    "type":    "application/x-octet-stream"
               }
            }
        )

    def test_deserialize(self):
        self.doc.add_resource(
            Resource(path="/example", content="example")
        )
        self.doc.freeze()
        serial = self.doc.serialize()

        newdoc = Document(self.doc.name)
        newdoc.deserialize(serial)

        self.assertEqual(newdoc.resources.keys(), ['/example'])
        self.assertIsInstance(newdoc.resources['/example'], Resource)

        self.assertEqual(newdoc._originals.keys(), ['/example'])
        self.assertIsInstance(newdoc._originals['/example'], Resource)

    def test_callback(self):
        results = set()

        def callback_A(result):
            results.add("%r from A" % result)
        def callback_B(result):
            results.add("%r from B" % result)
        self.doc.set_callback('police_raid', callback_A)
        self.doc.set_callback('police_raid', callback_B)

        # Order is unpredictable for callbacks

        self.assertEqual(
            list(self.doc._callbacks.keys()),
            ['police_raid']
        )
        self.assertIsInstance(self.doc._callbacks['police_raid'], set)
        self.assertEqual(len(self.doc._callbacks['police_raid']), 2)
        for callback in self.doc._callbacks['police_raid']:
            self.assertIn(callback, (callback_A, callback_B))

        self.doc.trigger_callback(
            'police_raid',
            ["detective", "inspector"]
        )
        self.assertEqual(
            results,
            set([
                "['detective', 'inspector'] from A",
                "['detective', 'inspector'] from B",
            ])
        )

    def test_saving(self):
        self.doc.add_resource(
            Resource(path="/example", content="example")
        )
        self.doc.freeze()

        save_to(self.doc, "example.dje")
        newdoc = load_from("example.dje")
        self.assertEqual(newdoc.serialize(), self.doc.serialize())

class TestDocumentEJTP(unittest.TestCase):

    def setUp(self):
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

    def test_checkpoint(self):
        mcp = self.mdoc.checkpoint({
            'path':'/example',
            'property':'content',
            'value':'Mitzi says hi',
        })
        self.assertEqual(mcp.quorum.completion, 2)
        self.assertEqual(self.mdoc.competing, [])

        self.assertEqual(
            self.mdoc.get_resource('/example').content,
            "Mitzi says hi"
        )
        self.assertEqual(
            self.adoc.get_resource('/example').content,
            "Mitzi says hi"
        )

    def test_subscribe(self):
        # Test a read
        self.assertEqual(self.vdoc.version, 0)
        self.assertTrue(self.vdoc.can_read())

        # One error is normal, due to transmission patterns
        rr = self.vdoc.subscribe()
        # Error from '...@lackadaisy.com', code 40: ...'Unknown lock quorum data, dropping (ad4546b17ca708c051bd3619a4d688ea44873b9d)'
        self.assertEqual(self.mdoc.competing, [])
        self.assertEqual(self.adoc.competing, [])

        self.assertIsInstance(rr, ReadRequest)

        for doc in (self.mdoc, self.adoc):
            subscribers = doc.subscribers
            self.assertIsInstance(subscribers, set)
            self.assertEqual(len(subscribers), 1)
            self.assertIsInstance(list(subscribers)[0], Identity)
